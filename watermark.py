import os 
import glob
import cv2
from decimal import Decimal
from fractions import Fraction
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from PIL.ExifTags import TAGS
from pathlib import Path



def get_exif_info(image_path):
    # 打开图像文件
    image = Image.open(image_path)
    # 获取 EXIF 数据
    exif_data = image._getexif()
    if exif_data is not None:
        # 创建一个字典来存储所需的信息
        exif_info = {}
        # 遍历 EXIF 数据
        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag, tag)
            exif_info[tag_name] = value
        return exif_info
    else:
        print("No EXIF data found in the image.")


class Photo:
    def __init__(self,path):
        self.path = path
        self.name = os.path.basename(self.path)
        self.exif_info = get_exif_info(self.path)
    
    @property
    def img(self):
        # img = Image.open(self.path)
        # if 'Orientation' in self.exif_info:
        #     orientation = int(self.exif_info['Orientation'])
        #     if orientation==1:
        #         pass
        #     if orientation==8:
        #         img = img.rotate(90)
        img = cv2.imread(self.path)
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        return img

    @property
    def artist(self):
        return str(self.exif_info['Artist'])

    @property
    def camera_manufacturer(self):
        return str(self.exif_info['Make'])
    
    @property
    def camera_model(self):
        return str(self.exif_info['Model'])
    
    @property
    def lens_model(self):
        if 'LensModel' in self.exif_info:
            return str(self.exif_info['LensModel'])
    
    @property
    def lens_focal_length(self):
        if 'FocalLength' in self.exif_info:
            focal_length = int(self.exif_info['FocalLength'])
            return str(str(focal_length) + 'mm')
    
    @property
    def exp_aperture(self):
        if 'FNumber' in self.exif_info:
            fnumber = self.exif_info['FNumber']
            return str('f/' + '%.1f'%(fnumber))
    
    @property
    def exp_shutterspeed(self):
        if 'ExposureTime' in self.exif_info:
            tmp = self.exif_info['ExposureTime']
            tmp2 = Fraction(Decimal(str(tmp))).limit_denominator()
            return str(tmp2)
    
    @property
    def exp_iso(self):
        if 'ISOSpeedRatings' in self.exif_info:
            iso = int(self.exif_info['ISOSpeedRatings'])
            return str('ISO' + str(iso))
    
    @property
    def datetime(self):
        if 'DateTimeOriginal' in self.exif_info:
            datetime = self.exif_info['DateTimeOriginal']
            date = datetime.split(' ')[0].split(':')
            time = datetime.split(' ')[1].split(':')
            return str(date[0] + '-' + date[1] + '-' + date[2] + '  ' +
                    time[0] + ':' + time[1])
    
    @property
    def watermark_info(self):
        # Define the text to be printed
        left_info = [
            f"{self.camera_manufacturer} {self.camera_model}",
            f"{self.lens_model}"
        ]
        right_info = [
            f"{self.lens_focal_length} {self.exp_aperture} {self.exp_shutterspeed} {self.exp_iso}",
            f"{self.datetime}"
        ]
        return left_info, right_info
    
    @property
    def watermark_logo(self):
        band = self.camera_manufacturer.lower()
        logo_dir = 'logo/'
        pattern = os.path.join(logo_dir, f"*{band}*")
        matching_files = glob.glob(pattern, recursive=True)
        logo_img = Image.open(matching_files[0])
        return logo_img

    def add_watermark(self):
        img = self.img
        width, height = img.size
        left_text, right_text = self.watermark_info
        logo_img = self.watermark_logo
        
        # calculate border size based on the image size
        border_percentage = 0.03
        border_short = int(min(width, height)*border_percentage)
        border_long = border_short * 4

        # create a new image with a white border
        new_size = (width + 2*border_short, height + border_short + border_long)
        new_img = Image.new("RGB", new_size, "white")
        new_img.paste(img, (border_short, border_short))

        # prepare to draw text on the image
        draw = ImageDraw.Draw(new_img)
        text_height = border_short*0.75
        font_small = ImageFont.truetype('fonts/NotoSansSC-Light.ttf', text_height)
        font_large = ImageFont.truetype('fonts/NotoSansSC-Bold.ttf', text_height)

        # draw text
        left_text_position = (int(border_short*2), 
                              int(height + border_short*2))
        right_text_width = draw.textlength(right_text[0], font=font_large)
        right_text_position = (int(new_size[0] - right_text_width - border_short*2), 
                               int(height + border_short*2))

        line_height = border_short * 1
        for i, line in enumerate(left_text):
            if i == 0:
                draw.text(left_text_position, line, font=font_large, fill="black")
            else:
                draw.text(left_text_position, line, font=font_small, fill="black")
            left_text_position = (left_text_position[0], left_text_position[1] + line_height)
        for i, line in enumerate(right_text):
            if i == 0:
                draw.text(right_text_position, line, font=font_large, fill="black")
            else:
                draw.text(right_text_position, line, font=font_small, fill="black")
            right_text_position = (right_text_position[0], right_text_position[1] + line_height)

        # draw cutting line
        line_start = (int(right_text_position[0] - border_short), 
                      int(right_text_position[1]))
        line_end = (int(right_text_position[0] - border_short), 
                    int(right_text_position[1] - line_height * len(right_text)))
        draw.line([line_start, line_end], fill="black", width=int(border_short*0.05))

        # logo resize
        logo_height = int(border_short * 0.75)
        logo_width = int((logo_height / logo_img.height) * logo_img.width)
        logo_img = logo_img.resize((logo_width, logo_height))

        # draw logo
        logo_position = (int(right_text_position[0] - logo_width - border_short*2),
                         int(height + border_short * 2.7))
        new_img.paste(logo_img, logo_position)

        new_img.save('output/%s'%(self.name))
    

def get_jpg_files(folder_path):
    folder_path = Path(folder_path)
    if str(os.name) == 'nt':
        jpg_files = list(folder_path.glob('**\\*.jpg'))
        JPG_files = list(folder_path.glob('**\\*.JPG'))
        jpeg_files = list(folder_path.glob('**\\*.jpeg'))
    if str(os.name) == 'posix':
        jpg_files = glob.glob(os.path.join(folder_path, '*.jpg'))
        JPG_files = glob.glob(os.path.join(folder_path, '*.JPG'))
        jpeg_files = glob.glob(os.path.join(folder_path, '*.jpeg'))
    return jpg_files+JPG_files+jpeg_files


def process(folder_path):
    img_files = get_jpg_files(folder_path)
    img_num = len(img_files)
    for i in range(img_num):
        img = Photo(img_files[i])
        print(img.camera_manufacturer)
        img.add_watermark()


if __name__ == '__main__':
    folder_path  = 'image/'
    process(folder_path)