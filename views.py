

"""
Routes and views for the flask application.
"""
#-------iMPORTLAR---------------------------------------------------------------------------------------------------

import os                       # Sistem dosyalarina erisim icin import ettigim saf python modulu
import random					# crawl sisteminde her seferinde farkli sonuclar alabilmek adina ekledigim saf python modulu
import sys						# bunu flaskda web sitesini olustururken encode hatasinin cozumu olarak importladim.
import urllib					# Html sitelerimizden veri ceken bir modul
from flask import Flask, redirect, render_template, request, url_for # tum projenin internette calismasini saglayan modul
from smART import app			# Bu Flask icin gerekli __init__ verilerini almaya yariyor
from bs4 import BeautifulSoup	# Sonuclarin yaninda resim gostermek icin ekledim
import requests					# Beatiful soup importu ek eklentisi
##################################################################################################################
#--------------------DECODE--------------------------------------------------------------------------------------#
##################################################################################################################

reload(sys)						# Flaskta UTF8 Olmayan sonuclarda server kapanmasin diye decoce edip sistemi yeniden 
sys.setdefaultencoding('utf8')  #baslatmaya yariyan kisim

##################################################################################################################
#--------------------/get_page-Fonksiyonu\-----------------------------------------------------------------------#
##################################################################################################################
def get_page(url):
	try:
		r = urllib.urlopen(url)          		#urllib kutuphanesinin url acma fonksiyonuna urlleri gonderiyoruz
		page = r.read()							#sayfamizi urllib'in read fonksiyonu ile aciyoruz
		a = page.find("Page not found 404")   #Burada bir a degiskenine urllib'in okuma fonksiyonu ile sayfada 
		if a == -1:							  #Page Not Found 404 degeri aratiyorum.Bunun sebebi cok fazla hatali
			r.close()						  #404 sonucu cikarmasi.Burada listede 404 not found stringini bulamazsa
			return page						  #return page diyerek isleme devam ediyoruz.
		else:								  # ancak bu degeri bulursa bos string dondurerek o linklerden kurtuluyoruz.
			r.close()
			return ""
	except:	
		return ""							  # Burasi try kisimi calismazsa devreye girer ve bos string dondurur.
	return ""									# Bu kisim calisiyorsa muhtemelen urllib hata cikarmisdir
##################################################################################################################
#--------------------/Union-Fonksiyonu\--------------------------------------------------------------------------#
##################################################################################################################

def union(a,b):								   # Union fonksiyonu ismindende anlasilacagi uzere birlestirmeye yarar
	for e in b:								   # a ve b girdilerimiz olsun . Union bunlari toplar ama ayni string 
		if e not in a:						   # iki listedede varsa birini siler sadece birini ekler.
			a.append(e)						   # Bunu Crawlda kullanicagiz...

##################################################################################################################
#--------------------/get_next_url-Fonksiyonu\-------------------------------------------------------------------#
##################################################################################################################
def get_next_url(page):						   #get_next_url fonksiyonu sayfalari veriyoruz. 
											   #linklerin html'i a href ile baslar
	start_link=page.find("a href")			   #|a href| ile baslayan tum linkleri .find fonksiyonu ile bulucaz
	if(start_link==-1):						   # Eger sonuc bulamazsa link yok demektir. o zaman None ve 0 donduruyoruz
		return None,0
	start_quote=page.find('"',start_link)	   #Start_quote degiskenine ->(" ile a href'in) indexini atiyoruz
	end_quote=page.find('"',start_quote+1)	   #End_quote' a da -> ikinci tirnagi ve start_quotun index'i+1 atiyoruz 
	url=page[start_quote+1:end_quote]          #son olarakda bu index numaralari ile urlnin basindan sonuna secip
	return url,end_quote					   # url degiskenine atiyor ve url ile end_quote'i return ediyoruz
##################################################################################################################
#--------------------/get_all_links-Fonksiyonu\------------------------------------------------------------------#
##################################################################################################################
def get_all_links(seed, main_url, page):	   # seedi main_urlyi ve sayfayi alan ve tum Linkleri ceken bir fonksiyon
	links=[]								   # Bir Liste Tanimladik bu links listesine tum linkleri atacagiz.
	while(True):
		url,end_quote=get_next_url(page)	   # Bu kisimda get_next_url de return ettiklerimizi degiskenlere atiyoruz
		c = str(url)						   #url nin string haline c diyelim:
		x = c.find("/")						   #ve c'mizde "/" stringi arayalim cikani da x diye bir degiskene atalim.
		
		if x == 0:							   # eger "/" ilk indexteyse  url yi basa ekle
			url = main_url  + url[1:]		   # BUNU YAPMA SEBEBiM html de sayfa yonlendirmelerinde site ici sayfalarin
		page=page[end_quote:]				   #/about /contac seklinde urllere sahip olmasi ve bunu cektigimiz zaman 
		if url:								   #yeniden o link icinde crawl edemememiz.Bu yuzden ana_linki basina ekliyoruz.					
			links.append(url)				   # ve tekrar crawl ediyoruz (while).
		else:
			for z in links:					   #burasi adreste 404 ariyor yukarda get page'de anlattigim islemlerin aynisi
				eror = z.find("404")		   #burasi icinde gecerli
				if eror == -1:
					return links
				else:
					links.remove(eror)
			return links					   #En sonunda linklerimizi return ediyoruz.
##################################################################################################################
#--------------------/Look_up-Fonksiyonu\------------------------------------------------------------------------#
##################################################################################################################
def Look_up(index,keyword):					   # indexi ve aradigimiz kelimeyi look_up'a girdi olarak veriyoruz
	
	if keyword in index:					   # Eger keyword crawl edilen sayfanin index'inde varsa:
		return index[keyword]				   # keywordun indeksini cikar
	return []								   # yoksa bos liste cikar
##################################################################################################################
#--------------------/add_to_index-Fonksiyonu\-------------------------------------------------------------------#
##################################################################################################################
def add_to_index(index,url,keyword):		   #indexe ekleme yapan foksiyonumuz

	if keyword in index:					   #keywordumuz sozlugun icindeyse 
		if url not in index[keyword]:		   #ve url onceden indexin keyword bolumune eklenmediyse
			index[keyword].append(url)		   #index sozlugune url'i ekliyoruz
		return								   #ve cikariyoruz
	index[keyword]=[url]					   #sozlukte keywordumuzun karsiligini url listesine esitliyoruz
###################################################################################################################
#--------------------/add_page_to_index-Fonksiyonu\---------------------------------------------------------------#
###################################################################################################################
def add_page_to_index(index,url,content):      #bu fonksiyon sayfanin icerigini  bosluklara parcaliyip,
	for i in content.split():				   # her bir parcayi add_to_index fonksiyonunun ucuncu parametresi
		add_to_index(index,url,i)			   #(keyword) olarak gonderiyor
###################################################################################################################
#--------------------/compute_ranks-Fonksiyonu\-------------------------------------------------------------------#
###################################################################################################################
def compute_ranks(graph):					   #Bu Fonksiyon linklerimiz icin siralama hesabi yapar.
	d=0.8									   #Oncelikle d=0.8 sabitini belirliyoruz  bu Damping_factor udacity 0.8
											   #bende 0.8 aliyorum 1'den kucuk oldugu surece sikinti olmuyor.
	numloops=10								   # numloops=10  sabitini belirliyoruz
	ranks={}								   #burada ranks adinda bir sozluk olusturduk
	npages=len(graph)						   # npages adinda bir degisken icine graph sayisini atadik
	for page in graph:						   #graph sozlugunun icindeki her bir sayfayi:
		ranks[page]=1.0/npages				   #ranks sozlugunde ("rankdegeri":"sayfa" = 1/tekrar eden sayfa sayisi)
	for i in range(0,numloops):				   # Burada 0'dan 10'a kadar calisan bir for dongusu acip:
		newranks={}							   # yenirank sozlugu olusturduk
		for page in graph:					   # graph'in icindeki her bir sayfayi:
			newrank=(1-d)/npages			   # 1-sabit'e(0,8) bolup yenirank sozlugune esitliyoruz
			for node in graph:				   # graphtaki her bir dugum icin
				if page in graph[node]:		   # eger sayfa graph sozlugunun node'a karsilik gelen kismini barindiriyorsa:
					newrank=newrank+d*ranks[node]/len(graph[node]) #bu islemi yapiyor
			newranks[page]=newrank			   # 
		ranks=newranks						   # ranklari yeni ranlara esitliyor
	return ranks							   # ve fonksiyondan cikariyoruz
################################################################################################################
#--------------------/Loop breakers fonksiyoları\--------------------------------------------------------------#
################################################################################################################

def loop_breaker(url):
        start_url = url.find("/")
        find_slash = 0
        control = []
        while find_slash != -1:
                find_slash = url.find("/", start_url+1)
                find_other_slash = url.find("/", find_slash+1)
                dede = url[find_slash:find_other_slash]
                if dede not in control:
                        control.append(dede)
                else:
                        return False
                start_url = find_other_slash
        return True


def loop_for_loop_breaker(urls):
        new_urls = []
        for url in urls:
             if loop_breaker(url) == True:
                     new_urls.append(url)
        return new_urls
################################################################################################################
#--------------------/Crawl_web-Fonksiyonu\--------------------------------------------------------------------#
################################################################################################################
def Crawl_web(seed, max_limit):				   #Butun programimizin cekirdek fonksiyonu budur
	tocrawl=[seed]							   #Sayfalari gezer ve yazdigimiz fonksiyonlarin yuzde 60 i burada cagirilir.
	crawled=[]								   #seedleri liste halinde tocrawla atiyoruz ve birde crawled bos listesi
	index={}								   #olusturduk.Ayni zamanda yukarida anlattigim index ve graph
	graph={}								   #sozluklerini burada olusturuyoruz.
	while tocrawl:							   #-------Hadi While dogusu ile crawl islemine baslayalim----------------------
		tocrawl = loop_for_loop_breaker(tocrawl)
		p=tocrawl.pop()						   #crawl ediceklerimizi sondan alip p degiskenine atadim
		if len(tocrawl) % 2 == 0:			   #burda crawl edileceklerin sayisinin ikiye bolumu sifir oldugunda yani
			random.shuffle(tocrawl)			   #1/2 ihtimalle calisicak bir listeyi calkalama kodu yazdim.
											   #Bunu yazma nedenim: Crawl fonksiyonumuz belli bir limitle sinirli olmazsa
											   # Sonsuz donguye giriyor ve asla cikti vermiyor!.Mecburen crawli sinirlamamiz
											   # Gerekiyor ancak crawli sinirlama yaptigimizda sonuclar genelde bir site 
											   #uzerinde yogunlasiyor eger tum sitelerin oldugu listemizi calkalarsak 
											   # her seferinde farkli sonuclar almis ve daha verimli arama yapmis oluruz. 
											   #-----------------------------------------------------------------------------
		if p not in crawled:				   #burada pmiz crawledde yoksa
			max_limit-=1					   #arama limitimizi 1 dusuruyoruz
			if max_limit<=0:				   #eger arama limitimiz 0 a geldiyse:
				break						   # crawl while dongumuzu sonlandiriyoruz
			c=get_page(p)					   # p mizi yukarda anlattigim get_page fonksiyonuna gonderip c ye esitliyoruz
			add_page_to_index(index,p,c)	   #burada sayfalari indexe ekleme fonksiyonunu calistiyoruz
			f=get_all_links(seed, p, c)		   #tum linkleri al fonksiyonunu da cagirip ciktisini f e esitliyoruz
			union(tocrawl,f)				   #union fonksiyonunu cagirip unionda anlattigim birlestirmeyi yapiyoruz
			graph[p]=f						   #graph sozlugunda p nin karsiligini f ye esitliyoruz
			crawled.append(p)				   #ve En sonunda crawl ettiklerimizi crawled fonksiyonuna atiyoruz
	return index,graph						   #index ve graphi fonksiyonumuzdan cikariyoruz
##################################################################################################################
#--------------------/QuickSort-Fonksiyonu\----------------------------------------------------------------------#
##################################################################################################################

def QuickSort(pages,ranks):                    #Bu Fonksiyonumuz sayfalarimizi ranklara gore siralamaya yariyor
	if len(pages)>1:						   # Eger sayfa sayimiz 1 den buyukse(cunku baska turlu siralanmaz :)
		favori=ranks[pages[0]]				   # ranks sozlugumuzde pages listemizin ilk elemanini aliyoruz
		i=1									   # i diye bir sabit belirledim 
		for j in range(1,len(pages)):          # 1den sayfa sayisina kadar:
			if ranks[pages[j]]>favori:			   # Eger rank sozlugumuzun sayfa listesindeki j. indeksi favorimizden buyukse
				pages[i],pages[j]=pages[j],pages[i]#sayfa listesinin 2. elemanini ve j. elemanini yer degistir.
				i+=1						   #ve i degerini 1 artir
		pages[i-1],pages[0]=pages[0],pages[i-1] 
		QuickSort(pages[1:i],ranks)
		QuickSort(pages[i+1:len(pages)],ranks)
##################################################################################################################
#--------------------/Look_up_new-Fonksiyonu\--------------------------------------------------------------------#
##################################################################################################################
def Look_up_new(index,ranks,keyword):   	    #Look_up_new fonksiyonumuz ile artik programimizin sonuna yaklasiyoruz...
	pages=Look_up(index,keyword)				#Bu fonksiyon oncelikle look_up i calistirip kelimemizi ariyor
	urls = []									#urls listemizi burada tanimliyoruz
	print '\nSonuclar ranklara gore yazdiriliyor...\n' #
	for i in pages:                             	   # Burasi serverda arama sirasinda
		print i+" --> "+str(ranks[i])				   #			arama katmani hakkinda bilgi veriyor...
	QuickSort(pages,ranks)							   # Burasi siralama fonksiyonumuzu cagiriyor ve siraliyor
	print "\nAfter Sorting the results by page rank\n" #
	for i in pages:									   # sayfada listesindeki icindeki her elemani
		urls.append(i)								   # urls'e ekliyor ve urls i cikariyor boylece siralanmis hali de 
	return urls										   # tamamlaniyor
##################################################################################################################
#--------------------/Final-Fonksiyonu\--------------------------------------------------------------------------#
##################################################################################################################
def final(seed_page, search_term,max_limit):     #Geldik final fonksiyonumuza...Aranacak sayfayi,arama terimini,limiti aliyoruz
    index,graph=Crawl_web(seed_page,max_limit)	 #Crawl fonksiyonunu aranacak sayfamiz ve limitimiz girdisi ile cagirdik
    ranks = compute_ranks(graph)				 # ranklari hesapladik
    a = Look_up_new(index,ranks,search_term)	 #ve look up new ile kelime sorgusu + siralama algoritmasini calistirdik
    if a == []:									 #sonuc vermezse none cikar:
        return None
    return a									 # verirse cikarn sonucu return et dedik ve programin temel calisma 
	#											  kismini bitirdik burdan sonrasi bazi eklentilerim ve web sitesine 
	#                                             donusturme kisimi....
##################################################################################################################
#--------------------/lucky_search-Fonksiyonu\-------------------------------------------------------------------#
##################################################################################################################
def lucky_search(seed_page, search_term,max_limit): #Bu kisim Google'da oldugu gibi ilk sonuc sitesine gitmemize yariyor
        b=final(seed_page, search_term,max_limit)	#final fonksiyonumuzun ciktilarini b'ye atadik
        if b == None:  								# sonuc yoksa none ver dedim
                return None
        return b[0]									# sonuc varsa listenin ilk elemanini al ve fonksiyondan cikar.
##################################################################################################################
#--------------------/get_title-Fonksiyonu\-----------------------------------------------------------------------
##################################################################################################################
def get_title(urls):								#Bu kisim arama sonuclarinda her sitenin basligini cekiyor.
	if urls == None:							    # Eger url yoksa none dondur.
		return None
	titles = []									    # titles adinda bir liste olusturdum sayfalari buraya aticam
	for url in urls:								# Urllerin icindeki her url icin
		x = urllib.urlopen(url)						#url libi cagirdim ve her urlyi acip x'e attim
		page = x.read()								
		start_title = page.find('<title>')			#htmlde sayfa basliklari title olur bu yuzden title tagi aratiyorum
		end_title = page.find('</', start_title+1)	#buraya kadar seciyorum
		title = page[start_title+7:end_title]		#en son burada baslik halini aliyor
		titles.append([url, title]) 				# url ile birlikte title listesine ekliyorum
	return titles									#Title lsitesini cikariyorum
##################################################################################################################
#--------------------/get_pictures-Fonksiyonu\-------------------------------------------------------------------#
##################################################################################################################
def get_pictures(urls,pictures):					#Bu fonksiyonu sonuclar yaninda sitenin varsa bir resmini koymak
	if urls != None:								#icin yazdim. eger urls degeri none ise calis yoksa resim kismini atla
		for url in urls:							#dedim.Ve bir for dogusu acip urllerin icindeki her url icin
			content = requests.get(url).content		#urlden icerik aldim
			soup = BeautifulSoup(content, 'lxml')   #onceki yollardan farkli olarak burda beatifullsoup eklentisi ile
			image_tags = soup.findAll('img', limit = 1) # image taglarini ve linklerini buldurdum cunku daha hizli calisiyor
			if image_tags == [] or None or "":			# limit kisimi her siteden kac resim istedigini belirliyor.
				break									#burada eger image tags bos kumeyse donguden cikiyoruz
			for image_tag in image_tags:				#ilk for da imgleri aldik simdi onlarin url'lerini alalim..
				a = image_tag.get("src")				# bu get("src") fonksiyonu imagelerden url aliyor
				if a == None:							# eger a None ise resim yok diyor
					a == "No Picture"
					continue
				else:									#degilse pictures adinda birlisteye ekliyor ve return ediyoruz
					pictures.append(a)
			return pictures
	else:
		return
##################################################################################################################
#--------------------/App.Route ve Html'e Gidecekler\------------------------------------------------------------#
##################################################################################################################
@app.route("/")										   # Burada app.route ile html sayfasina yonlendirme yapiyoruz
def index():										   # Anasayfayi tanimladim
    return render_template("index.html")			   # render template ile html dosyami python serverime attim
@app.route("/about")								   # Hakkimda sayfasi icin yonlendirme..
def about():										   # Hakkimda sayfasini tanimladim
        return render_template("about.html")		   # render template ile html dosyami python serverime attim
@app.route("/advise")								   # advise tavsite sayfasi yonlendirmesi..
def advise():										   # advise tavsiye sayfasini tanimladim
        return render_template("suggestions.html")	   # render template ile html dosyami python serverime attim
@app.errorhandler(404)
def page_not_found(e):								   # Burada 404 hatasi cikarsa diye bir sayfa olusturdum
    return render_template('404.html'), 404
@app.errorhandler(500)								   # Burada server hatasi cikarsa 404 e yonlendirdim
def server_error(e):
	return render_template('404.html'), 500

@app.route("/search", methods = ["GET", "POST"])	   # GET,POST Methodlari ile html formlarindan veri cekme kisimi:
def search():										   # arama sayfasi tanimladim
        if request.method == "POST":				   # eger post methoduysa
                if request.form["action"] == "search":  ## Eger SEARCH BUTONUNA BASARSAK:
                        seed = request.form.get("seed")   # seed formumdan seedi al
                        keyword = request.form.get("keyword")	# keyword formumdan keywordu al
                        max_limit = int(request.form.get("searching_limit")) #scroll bardan searching limiti al.
                        urllist = final(seed, keyword, max_limit)  # urllist'i finalde hesapla
                        urlwhittitle = get_title(urllist)	#ve get title ile basliklari al
                        pictures = []						# pictures adinda bos bir liste olusturduk
			pic_url = get_pictures(urllist,pictures)		# get_pictures ile resimleri alip pic_urlye atadim

                        return render_template("chosesite.html", urlwhittitle = urlwhittitle ,pic_url = pic_url )
        elif request.form["action"] == "luck":        # Eger I FEEL LUCKY  butonuna basarsak
                seed = request.form.get("seed")
                keyword = request.form.get("keyword")
                max_limit = int(request.form.get("searching_limit"))
                sans  = lucky_search(seed, keyword,max_limit)  # lucky search fonksiyonunu calistirip sans'a attim
                print os.system("start chrome " + sans  + "/&amp;") # os modulu ile yeni sekmede ilk sonucu actirdim"
                return render_template("chosesite.html", urllist = final(seed, keyword,max_limit)) # eski sekmede diger sonuclari listelettim
                
                

        else:
                return redirect(url_for("index"))
##################################################################################################################
