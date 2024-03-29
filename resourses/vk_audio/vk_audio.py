from .audio_obj import *
from .audio import *
from .audio_enum_index import *
import json as json_parser
import vk_api, json, random
# import vk_audio_C_FUNC as func_c
class VkAudio(object):
    @property
    def _enum_p(self):
        if(not self.__enum_p):self.__enum_p=AudioEnumIndex(
            html.fromstring(self.vk.http.get('https://vk.com/').text).head, self.vk)
        return self.__enum_p;
    def __init__(self,vk=None,login=None,password=None,remixsid_cookie=None,count_audios_to_get_url=10,your_id=None):
        """Модуль аудио вк. 
            :param vk: сессия vk_api.VkApi или login и пароль
            :param count_audios_to_get_url: У скольких аудио получать ссылки за раз. Чем меньше значение, тем быстрее будут получаться ссылки. Устанавливать значение в пределах 1-10
            :param remixsid_cookie: Кука remixsid, которую можно взять из браузера. Один из вариантов авторизации.
            :param your_id: Ваш id. При указании неверного id могут получиться неиграбельные ссылки. Если не указан - берется либо из токена либо методом users.get
            """
        if login is not None and password is not None:
            vk = self.vk=vk_api.VkApi(login,password);
            self.vk.auth()
        elif vk is not None:
            self.vk=vk;
        elif remixsid_cookie is not None:
            vk = self.vk = vk_api.VkApi()
            vk.http.cookies.set("remixsid",remixsid_cookie)
            if(your_id is None):raise ValueError("If you're auth with cookie your_id should be not None")
            from warnings import warn
            warn("Be careful - you may get some wierd errors - the may happend because cookie is invalid or out of date",UserWarning)
        else:raise ValueError("No auth data passed");
        self.uid = your_id or ('user-id' in self.vk.token and self.vk.token['user-id']) or self.vk.method("users.get")[0]["id"] #Аналогично коду your_id if your_id else ...
        self.c_u = count_audios_to_get_url
        self.__enum_p=None
    def load(self,owner_id=None) -> Audio:
        """
        Получить музыку пользователя/группы вк.
        :param owner_id: id страницы, у которой хотите получить аудио. Для групп - отрицательный
        :type owner_id: int or NoneType
        :param count_audios_to_get_url: У скольких аудиозаписей получать ссылку за один раз
        :type count_audios_to_get_url: int
        """
        if(owner_id is None):owner_id=self.uid

        html_text = self.vk.http.get('https://vk.com/audios%i' % owner_id,allow_redirects=False).text;
        if(not html_text):return False
        tree = html.fromstring(html_text)

        if(not self.__enum_p):self.__enum_p=AudioEnumIndex(tree.head,self.vk)
        script_with_info = self._get_script_el(tree);
        if(script_with_info==False):return False;

        #получаем данные о плейлисте в json
        json = self._parse_json_from_js(script_with_info.text)
        audio_to_return = (MyAudio if bool(json['newPlaylistHash']) else Audio)(self,owner_id,json['reorderHash'],json['audiosReorderHash'],json['newPlaylistHash'],json['listenedHash'],json['playlistCoverUploadOptions'])
        audio_to_return.load_playlists_from_js(json['playlists']);
        if 'playlist' in json['sectionData']['all'] and json['sectionData']['all']['playlist'] and json['sectionData']['all']['playlist']['list']:
            audio_to_return.load_audios_from_js(json['sectionData']['all']['playlist']['list']);
        return audio_to_return
    def load_artist(self,artist_nickname=None,artist_id=None,artist_hash=None) -> Audio:
        """
        Получение музыки артиста. Возможно без авторизации
        :param artist_nickname: Никнейм артиста.
        :type artist_nickname: str or NoneType
        :param artist_id: Id артиста.
        :type artist_id: int or NoneType
        """
        if(artist_hash is not None):
            if(artist_hash.startswith("s")):return self.search(query = artist_hash[1:])
            elif(artist_hash.startswith("a")):artist_nickname=artist_hash[1:]
            elif(artist_hash.startswith("i")):artist_id=artist_hash[1:]
            else:raise ValueError("Invalid artist hash - you have to get it from method zip_artist in Playlist or AudioObj")
        artist_href = ""
        if(artist_nickname is not None): 
            if("/" not in artist_nickname):artist_href = "artist/"+artist_nickname
            else:artist_href=artist_nickname
        elif(artist_id is not None): artist_href = "artist/"+str(artist_id)
        else:raise ValueError("artist_nickname or artist_id should be not None");

        h = html.fromstring(self.vk.http.get("https://vk.com/al_artist.php", allow_redirects=False, params={
            "__query":artist_href+"/top_audios",
            "_ref":artist_href,
            "_rndVer":random.randint(0,100000),
            "al":-1,
            "al_id":self.uid
            }).text).head.getchildren();
        if(len(h)!=3):raise vk_api.AccessDenied("Artist not found")
        json_audios = self._parse_json_from_js(h[1].text);
        if(not json_audios):raise vk_api.AccessDenied("Artist not found")
        if(json_audios['payload'][1][0].startswith('"\/artist\/')):
            return self.load_artist(json_audios['payload'][1][0].strip('"\'').replace("\\","").lstrip("/"))
        audios_html = html.fromstring(json_audios['payload'][1][1]);
        h = html.fromstring(self.vk.http.get("https://vk.com/al_artist.php", allow_redirects=False, params={
            "__query":artist_href+"/albums",
            "_ref":artist_href,
            "_rndVer":random.randint(0,2147483647),
            "al":-1,
            "al_id":self.uid
            }).text).head.getchildren()
        albums_html = None
        if(len(h)==3):  
            json_albums = self._parse_json_from_js( h[1].text)
            albums_html = html.fromstring(json_albums['payload'][1][1]);
        return ArtistAudio(self,audios_html,albums_html,artist_nickname);
    def search(self,query="Imagine dragons") -> AudioSearch:
        resp = self._action(data= {
            'act': 'section',
            'al': 1,
            'claim': 0,
            'is_layer': 0,
            'owner_id': self.uid,
            'q': query,
            'section': 'search'
        });
        a = AudioSearch(self,resp['payload'][1][0])
        # print(a.__dict__)
        # print(a._html)
        result = a.load_playlists_from_html(a._html);
       
        return result;
    def get_only_audios(self,owner_id=None,offset=0):
        """Получение аудиозаписей пользователя ( или группы )
        :param owner_id: id пользователя ( или группы )
        :type owner_id: int or NoneType
        :param offset: смещение
        :type offset: int
        """
        if(owner_id is None ): owner_id=self.uid
        return Audio.load_audios(self,offset,owner_id=owner_id)
    def get_by_id(self,audios):
        '''
        Получить аудиозапись по id
        :param audios: Аудиозаписи, которые надо получить перечисленные через запятую ( или в виде списка ).
        :type audios: str or list
        '''
        if(isinstance(audios,str)):audios = audios.split(",")
        ans,auds = [],[]
        c = 0;
        for i in audios:
            url = 'https://m.vk.com/audio'+i;
            response = self.vk.http.post(url);
            h = html.fromstring(response.text).find_class("audio_item_" + i)
            if(not h):
                ans.append(False)
            else:
                o = AudioObj.parse(json_parser.loads(h[0].attrib['data-audio']),self,auds);
                ans.append(o)
                auds.append(o)
                c+=1
                if(c%10==9):
                    auds = []
        return ans;
    def _get_script_el(self,tree):
        for i in tree.body.getchildren()[::-1]:
            if(i.tag=='script'):
                return i
        return False
    def _parse_json_from_js(self,js):
        if(not isinstance(js,str)):raise TypeError("js have to be str")
        # q = func_c.parse_json_from_js(js);
        q=''
        return json_parser.loads(q)


    @staticmethod
    def json(resp):
        try:
            return json_parser.loads(resp.text.lstrip('<!--'))
        except json.decoder.JSONDecodeError:
            pass
    def _action(self,url="https://vk.com/al_audio.php",data={},params={},method="post",**args):
        from .vk_audio import VkAudio
        r = self.vk.http if(isinstance(self,VkAudio)) else self.http if isinstance(self,vk_api.VkApi) else self
        r.headers['X-Requested-With']='XMLHttpRequest'
        f=(r.post if method=="post" else r.get)
        resp = f(url,data=data,params=params,**args)
        del r.headers['X-Requested-With'];

        json = VkAudio.json(resp);
        json["success"]=(json and 'payload' in json and len(json['payload'])>=2 and len(json['payload'][1])!=0)

        return json
