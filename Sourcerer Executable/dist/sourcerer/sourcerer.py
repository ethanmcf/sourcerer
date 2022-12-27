import kivy
from kivy import context
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder

import time
from datetime import date
from bs4 import BeautifulSoup
import requests

style = "mla"


class InputScreen(Widget):
    doc = ObjectProperty(None)

    def errorPopup(self):
        error = MyErrorPopup()
        window = Popup(title="Not all websites could be cited!",content=error, size_hint=(None,None),size=(600,200))
        window.open()
    
    def needWebsitesPopup(self):
        remind = MyWebsitePopup()
        window = Popup(title="Whoa there!",content=remind,size_hint=(None,None),size=(300,200))
        window.open()
    
    def getInfo(self,link,style):
        return_info = []

        #Set up for beaufiul soup parsing
        number = link.split(":")[0]
        headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"}
        url=link[link.index("h"):]
        cite = requests.get(url,headers=headers, timeout=18).content
        soup = BeautifulSoup(cite,'html.parser')

        #Configure title
        titled = soup.find("meta", property="og:title")
        if str(titled) == "None":
            title = soup.find('title').get_text().strip() 
            if "|" in str(title):
                title = title.split("|")[0] 
        else:
            title = titled['content']
            if "|" in str(title):
                title = title.split("|")[0] 
        if "â€™" in title:
            title = title.replace("â€™","'")
            
        #Configure Url
        web_urled = soup.find("meta", property="og:url")
        if str(web_urled) == "None":
            web_url = url
        else:
            web_url = web_urled['content']
        
        #Configure website name
        cite_named = soup.find("meta", property="og:site_name")
        if str(cite_named) == "None":
            cite_name = ""
        else:
            cite_name = cite_named['content']
        #Configure publish date
        published = soup.find("meta", property="article:modified_time")
        if str(published) == "None":
            published = soup.find("meta", property="article:published_time")
            if str(published) == "None":
                publish = ""
            else:
                publish = published['content']
        else: 
            publish = published['content']    
            
        #Configure author
        authored = soup.find('meta',attrs={'name':'author'})
        if str(authored) == "None":
            authored = soup.find('div',attrs={'class':'author-name'})
            if str(authored) == "None":
                author = ""
            else:
                author = authored.get_text().lower()
        else:
            author = authored['content']
        if "by" in author:
            author = author.replace("by","").strip().title()


        if style == "mla":
            date = self.fixMLATime(publish)
            web_url = self.stripUrl(web_url)
        else:
            date = self.fixAPATime(publish)

        return_info.append(author)
        return_info.append(cite_name)
        return_info.append(title)
        return_info.append(date)
        return_info.append('')
        return_info.append(web_url)
        return_info.append(number)

        return return_info

    def inTextMLACites(self,doc,cites):
        intext = ''
        for z in range(0,len(doc)):
            if doc[z:z+5].lower() == "(cite":
                start = z+1 
            if doc[z] == ")":
                end = z
                text = doc[start:end].replace(" ","")
                for j in range(len(cites)):
                    if text.lower() == cites[j][:cites[j].index(":")].lower():
                        url_info = self.getInfo(cites[j][cites[j].index("h"):],"mla")
                        author = url_info[0]
                        title = url_info[2]
                        if len(author) != 0:
                            if "" in author:
                                intext = author.split(" ")[1]
                            else:
                                intext = author
                        elif len(title) !=0:
                            intext = '"' + title + '"'
                        else:
                            intext = "***COULD NOT CITE***"
                        count = 0
                        for spaces in intext:
                            if spaces == " ":
                                count += 1
                        if count > 3:
                            intext = intext.replace(" an "," ")
                            intext = intext.replace(" An "," ")
                            intext = intext.replace("An ", "")
                            intext = intext.replace(" a "," ")
                            intext = intext.replace(" A "," ")
                            intext = intext.replace(" the"," ")
                            intext = intext.replace("The ", "")
                            intext = intext.replace(" The "," ")
                            intext = intext.replace(" of ", " ")
                            intext = intext.replace(" Of ","")
                            intext = intext.replace("Of ","")
                        count2 = 0
                        for spaces2 in intext:
                            if spaces2 == " ":
                                count2 += 1
                        if count2 > 3:
                            intext = intext.split(" ")[0] +" " + intext.split(" ")[1] + " " + intext.split(" ")[2] + " " + intext.split(" ")[3] + '"'

                        doc = doc[:start] + intext + doc[end:]
        return doc     
    
    def inTextAPACites(self,doc,cites):
        intext = ''
        for z in range(0,len(doc)):
            if doc[z:z+5].lower() == "(cite":
                start = z+1 
            if doc[z] == ")":
                end = z
                text = doc[start:end].replace(" ","")
                for j in range(len(cites)):
                    if text.lower() == cites[j][:cites[j].index(":")].lower():
                        url_info = self.getInfo(cites[j][cites[j].index("h"):],"apa")
                        author = url_info[0]
                        date = url_info[3]
                        title = url_info[2]
                        if len(author) != 0:
                            if " " in author:
                                intext = author.split(" ")[1]
                            else:
                                intext = author
                        elif len(title) !=0:
                            intext = '"' + title + '"'
                        else:
                            intext = "***COULD NOT CITE***"
                        count = 0
                        for spaces in intext:
                            if spaces == " ":
                                count += 1
                        if count > 3:
                            intext = intext.replace(" an "," ")
                            intext = intext.replace(" An "," ")
                            intext = intext.replace("An ", "")
                            intext = intext.replace(" a "," ")
                            intext = intext.replace(" A "," ")
                            intext = intext.replace(" the"," ")
                            intext = intext.replace("The ", "")
                            intext = intext.replace(" The "," ")
                            intext = intext.replace(" of ", " ")
                            intext = intext.replace(" Of ","")
                            intext = intext.replace("Of ","")
                        count2 = 0
                        for spaces2 in intext:
                            if spaces2 == " ":
                                count2 += 1
                        if count2 > 3:
                            intext = intext.split(" ")[0] +" " + intext.split(" ")[1] + " " + intext.split(" ")[2] + " " + intext.split(" ")[3] + '"'
                        if len(date) != 0:
                            intext += ", " + date.split(",")[0].replace("(","")
                        else:
                            intext += ", n.d." 

                        doc = doc[:start] + intext + doc[end:]
        return doc           
            
    def removeInTextMark(self,lst):
        removed_lst = []
        for marks in lst:
            marks = marks.split("~")[0]
            removed_lst.append(marks)
        return removed_lst
    
    def getFormat(self,instance,value,formatted):
        global style
        if formatted == "apa":
            style = formatted
            self.ids.apa.outline_color = (189/255, 115/255, 240/255,1)
            self.ids.apa.color = 1,1,1
            self.ids.apa.font_size = 26
            self.ids.apa.outline_width = 4

            self.ids.mla.outline_color = (1,1,1)
            self.ids.mla.outline_width = 2
            self.ids.mla.font_size = 23
            self.ids.mla.color = (189/255, 115/255, 240/255,1)
        elif  formatted == "mla":
            style = formatted
            self.ids.apa.outline_color = (1,1,1)
            self.ids.apa.outline_width = 2
            self.ids.apa.font_size = 23
            self.ids.apa.color = (189/255, 115/255, 240/255,1)

            self.ids.mla.outline_color = (189/255, 115/255, 240/255,1)
            self.ids.mla.color = 1,1,1
            self.ids.mla.font_size = 26
            self.ids.mla.outline_width = 4
        else:
            return style
        
    def startCite(self):
        #Get document info
        output = False
        url = self.doc.text
        self.ids.cite.source = "images/wizard.png"
        website_list = []
        lst = self.identifyUrls(url)
        if len(lst) == 0:
            self.needWebsitesPopup()
        else:
            time.sleep(1.5)
            #Get info from kivy user
            forms = self.getFormat("","","")
            if forms == "mla":
                for link in lst:
                    info = self.getInfo(link,"mla")
                    website_list.append(self.createMLACitation(info))

                website_list = self.citeSort(website_list)

                new_doc = self.inTextMLACites(url,lst)

                website_list = self.removeInTextMark(website_list)
                for web in website_list:
                    if "***" in web:
                        output = True

                self.recreateDoc(new_doc,website_list)
                time.sleep(1.5)
                if output == True:
                    self.errorPopup()
            else:
                for link in lst:
                    info = self.getInfo(link,"apa")
                    website_list.append(self.createAPACitation(info))

                website_list = self.citeSort(website_list)

                new_doc = self.inTextAPACites(url,lst)

                website_list = self.removeInTextMark(website_list)
                for web in website_list:
                    if "***" in web:
                        output = True

                self.recreateDoc(new_doc,website_list)
                time.sleep(1.5)
                if output == True:
                    self.errorPopup()

    def recreateDoc(self,doc,lst):
        finish = False
        for c in range(len(doc)):
            if (doc[c:c+4].lower() == "cite" and doc[c+4].isdigit() == True and doc[c+5] == ":") and finish == False:
                ind = c
                break
            elif (doc[c:c+4].lower() == "cite" and doc[c+4].isdigit() == True and doc[c+5].isdigit() == True and doc[c+6] == ":") and finish == False:
                ind = c
                break
        ref_lst = ''
        for citations in lst:
            ref_lst += citations + "\n\n"
        back = doc[:ind] + ref_lst
        self.doc.text = back

    def citeSort(self,lst):
        for i in range(len(lst)):
            if '"' in lst[i]:
                if lst[i].index('"') == 0:
                    lst[i] = lst[i].replace('"','',1)
                    lst[i] = lst[i].replace('"',"@")
        lst.sort()
        for j in range(len(lst)):
            if "@" in lst[j]:
                lst[j] = lst[j].replace("@",'"')
                lst[j] = '"' + lst[j]
            if "AAAAAAAAAAAAAAA" in lst[j]:
                temp = lst[j].split("~")[1]
                temp2 = lst[j].split("~")[0]
                lst[j] = temp2.replace("AAAAAAAAAAAAAAA", "***COULD NOT WORK MAGIC FOR: ") + "***" +"~" + temp + "~"
        return lst

    def stripUrl(self,url):
        url = url.replace("https://","")
        return url

    def createMLACitation(self,lst):
        author = lst[0]
        cite_name = lst[1]
        title = lst[2]
        pubdate = lst[3]
        publisher = lst[4]
        url = lst[5]
        num = lst[6]
        dateacc = date.today().strftime("%d %B %Y.")
        dateacc = "Accessed " + str(dateacc.split(" ")[0]) + " " + str(dateacc.split(" ")[1][:3]) + ". " + str(dateacc.split(" ")[2])
        space = " "
        if len(author) + len(title) + len(cite_name) + len(pubdate) + len(publisher) == 0:
            created = "AAAAAAAAAAAAAAA" + url + "~" +num
        else:
            if len(author) != 0 and (space in author):
                author = author.split(" ")[1] + ", " + author.split(" ")[0] +"."
            elif len(author) != 0:
                author += "."
            if len(title) != 0 and len(author) != 0:
                title = ' "' + title + '".'
            elif len(title) != 0:
                title = '"' + title + '".'
            if len(cite_name) != 0:
                cite_name += ","
            if len(publisher) != 0:
                publisher += ","
            created = '{}{} {} {} {} {}. {} ~{}~'.format(author,title,cite_name,publisher,pubdate,url, dateacc, num)
        return created

    def createAPACitation(self,lst):
        author = lst[0]
        cite_name = lst[1]
        title = lst[2]
        pubdate = lst[3]
        publisher = lst[4]
        url = lst[5]
        num = lst[6]
        dateacc = date.today().strftime("%d %B %Y.")
        dateacc = "Accessed " + str(dateacc.split(" ")[0]) + " " + str(dateacc.split(" ")[1][:3]) + ". " + str(dateacc.split(" ")[2])
        space = " "
        if len(author) + len(title) + len(cite_name) + len(pubdate) + len(publisher) == 0:
            created = "AAAAAAAAAAAAAAA" + url + "~" +num
        else:
            if len(author) != 0 and (space in author):
                author = author.split(" ")[1] + ", " + author.split(" ")[0][0] +"."
            elif len(author) != 0:
                author += "."
            if len(title) != 0:
                title += '.'
            if len(cite_name) != 0:
                cite_name += "."
            if len(pubdate) == 0:
                pubdate = "(n.d.)."
            if len(author) == 0:
                created = '{} {} {} {} ~{}~'.format(title,pubdate,cite_name,url,num)
            else:
                created = '{} {} {} {} {} ~{}~'.format(author,pubdate,title,cite_name,url,num)
        return created
    
    def fixMLATime(self,date):
        publish = ""
        if "T" in date:
            date = date.split("T")
            d = date[0].split("-")
            year = d[0]
            day = d[2]
            dlst = ['01','02','03','04','05','06','07','08','09','10','1','12']
            mlst = ['Jan.','Feb.','Mar.','Apr.','May','Jun.','Jul.','Aug.','Sep.','Oct.','Nov.','Dec.']
            for i in range(len(dlst)):
                if dlst[i] == d[1]:
                    month = mlst[i] 
            publish = "{} {} {},".format(day,month,year)

        if "/" in date:
            date = date.split("/")
            month = date[0]
            if len(month) == 1:
                month = "0" + month
            day = date[1]
            if len(day) == 1:
                day = "0" + str(day)
            year = date[2][:5]
            dlst = ['01','02','03','04','05','06','07','08','09','10','1','12']
            mlst = ['Jan.','Feb.','Mar.','Apr.','May','Jun.','Jul.','Aug.','Sep.','Oct.','Nov.','Dec.']
            for i in range(len(dlst)):
                if dlst[i] == month:
                    month = mlst[i] 
            publish = "{} {} {},".format(day,month,year)
        return publish

    def fixAPATime(self,date):
        publish = ""
        if "T" in date:
            date = date.split("T")
            d = date[0].split("-")
            year = d[0]
            day = d[2]
            dlst = ['01','02','03','04','05','06','07','08','09','10','1','12']
            mlst = ['January','February','March','April','May','June','July','August','September','October','November','December']
            for i in range(len(dlst)):
                if dlst[i] == d[1]:
                    month = mlst[i] 
            publish = "({}, {} {}).".format(year,month,day)

        if "/" in date:
            date = date.split("/")
            month = date[0]
            if len(month) == 1:
                month = "0" + month
            day = date[1]
            if len(day) == 1:
                day = "0" + str(day)
            year = date[2][:5]
            dlst = ['01','02','03','04','05','06','07','08','09','10','1','12']
            mlst = ['January','February','March','April','May','June','July','August','September','October','November','December']
            for i in range(len(dlst)):
                if dlst[i] == month:
                    month = mlst[i] 
            publish = "({}, {} {}).".format(year,month,day)
        return publish

    def identifyUrls(self,urls):
        start = -1
        website_urls = []
        urls = urls.replace(" ","")
        for chars in range(len(urls)):
            if (urls[chars:chars+4].lower() == "cite" and urls[chars+4].isdigit() == True and urls[chars+5] == ":"):
                start = chars
            elif (urls[chars:chars+4].lower() == "cite" and urls[chars+4].isdigit() == True and urls[chars+5].isdigit() == True and urls[chars+6] == ":"):
                start = chars
            if (urls[chars] == "\n" or chars+1 == len(urls)) and start != -1: 
                website_urls.append(urls[start:chars+1].strip())
                start = -1 
        return website_urls

    def clear(self):
        self.doc.text = ""
    
    def changeButton(self):
        self.ids.cite.source = "images/wizard_pressed.png"

class MyWebsitePopup(BoxLayout):
    pass
class MyErrorPopup(BoxLayout):
    pass

class Sourcerer(App):
    def build(self):
        return InputScreen()

if __name__ == '__main__':
    Sourcerer().run()