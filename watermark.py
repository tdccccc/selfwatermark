import exifread
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
def get_exif(IM):
    f=open(IM,'rb')
    tags=exifread.process_file(f)
    keynd=['Image Orientation','Image Make','Image Model','Image Artist','EXIF ExposureTime','EXIF FNumber','EXIF ISOSpeedRatings','EXIF FocalLength','Image DateTime']
    dic={key:value for key, value in tags.items() if key in keynd}
    if 'EXIF FNumber' in dict.keys(dic):
        dic['EXIF FNumber']=float(eval(str(dic['EXIF FNumber'])))
    for k in keynd[1:]:
        if k not in dict.keys(dic):
            dic[k]='-'
    return dic








class photo:
    def __init__(self,path):
        self.path=path

    @property
    def name(self):
        return(str(self.path).split('\\')[-1])
    @property
    def exif_dic(self):
        return(get_exif(self.path))
    @property
    def mkrstr(self):
        return(str(self.exif_dic['Image Make']))
    @property
    def mdlstr(self):
        return(str(self.exif_dic['Image Model']))
    @property
    def artstr(self):
        return(str(self.exif_dic['Image Artist']))
    @property
    def ori(self):
        if 'Image Orientation' in dict.keys(self.exif_dic):
            return(self.exif_dic['Image Orientation'].values[0])
        else:
            return('-')
    @property
    def exstr(self):
        return(str(self.exif_dic['EXIF ExposureTime'])+'s'+'  f/'+str(self.exif_dic['EXIF FNumber'])+'  ISO '+str(self.exif_dic['EXIF ISOSpeedRatings'])+"  "+str(self.exif_dic['EXIF FocalLength'])+'mm')
    @property
    def tmstr(self):
        time=str(self.exif_dic['Image DateTime']).split(":")
        if time[0] !='-':
            tm=time[0]+"/"+time[1]+"/"+time[2]+":"+time[3]+":"+time[4]
        else: 
            tm = '-'
        return(tm)
    @property
    def img(self):
        iminit=Image.open(self.path)
        i=self.ori
        if i==8:
            im=iminit.transpose(Image.Transpose.ROTATE_90)
        elif i==7:
            imi=iminit.transpose(Image.Transpose.ROTATE_270)
            im=imi.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        elif i==6:
            im=iminit.transpose(Image.Transpose.ROTATE_270)
        elif i==5:
            imi=iminit.transpose(Image.Transpose.ROTATE_270)
            im=imi.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        elif i==4:
            im=iminit.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        elif i==3:
            im=iminit.transpose(Image.Transpose.ROTATE_180)
        elif i==2:
            im=iminit.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        else:
            im=iminit
        return(im)



    def Pana_add_text(self):
        IM=self.img
        xsize , ysize =IM.size
        newim=Image.new(mode="RGB",size=(xsize,ysize+450),color=(255,255,255))
        newim.paste(IM)
        ft=ImageFont.truetype("arial.ttf",125)
        ftime=ImageFont.truetype("GARA.TTF",125)
        logo=Image.open('logo\\Lumix_Logo.jpg')
        newim.paste(logo,(75,ysize+150))
        LaIm=ImageDraw.Draw(newim)
        LaIm.text((1200,ysize+50),self.mkrstr,(0,0,0),ft)
        LaIm.text((1200,ysize+250),self.mdlstr,(0,0,0),ft)
        LaIm.text((xsize-1700,ysize+50),self.exstr,(0,0,0),ft)
        LaIm.text((xsize-1050,ysize+250),self.tmstr,(0,0,0),ftime)
        LaIm.text((700,ysize+50),self.artstr,(0,0,0),ft)
        return(newim)
    
    
    
    def Sony_add_text(self):
        IM=self.img
        xsize , ysize =IM.size
        newim=Image.new(mode="RGB",size=(xsize,ysize+450),color=(255,255,255))
        newim.paste(IM)
        ft=ImageFont.truetype("arial.ttf",125)
        ftime=ImageFont.truetype("GARA.TTF",125)
        logo=Image.open('logo\\sony-alpha.jpg')
        newim.paste(logo,(75,ysize+150))
        LaIm=ImageDraw.Draw(newim)
        LaIm.text((600,ysize+50),self.mkrstr,(0,0,0),ft)
        LaIm.text((600,ysize+250),self.mdlstr,(0,0,0),ft)
        LaIm.text((xsize-1700,ysize+50),self.exstr,(0,0,0),ft)
        LaIm.text((xsize-1050,ysize+250),self.tmstr,(0,0,0),ftime)
        LaIm.text((700,ysize+50),self.artstr,(0,0,0),ft)
        return(newim)
    

    def Oth_add_text(self):
        IM=self.img
        xsize , ysize =IM.size
        newim=Image.new(mode="RGB",size=(xsize,ysize+450),color=(255,255,255))
        newim.paste(IM)
        ft=ImageFont.truetype("arial.ttf",125)
        ftime=ImageFont.truetype("GARA.TTF",125)
        LaIm=ImageDraw.Draw(newim)
        LaIm.text((100,ysize+50),self.mkrstr,(0,0,0),ft)
        LaIm.text((100,ysize+250),self.mdlstr,(0,0,0),ft)
        LaIm.text((xsize-1700,ysize+50),self.exstr,(0,0,0),ft)
        LaIm.text((xsize-1050,ysize+250),self.tmstr,(0,0,0),ftime)
        return(newim)
    


    def add_text(self):
        if self.mkrstr=='SONY':
            im=self.Sony_add_text()
        elif self.mkrstr=='Panasonic':
            im=self.Pana_add_text()
        else:
            im=self.Oth_add_text()
        return(im)
    

def process(file_path):
    li=Path(file_path)
    Li=list(li.glob('**\\*.JPG'))
    for i in range(0,len(Li)):
        a=photo(Li[i])
        print(a.mkrstr)
        a.add_text().save('output\\'+a.name)


paths=input("input folder path to add watermark//请输入需要添加水印的文件夹")
process(paths)