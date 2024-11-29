import base64
from PIL import Image
from io import BytesIO

def base64ToPng():
    # 你的 base64 编码的图片字符串
    base64_string = "data:image/png;base64,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"

    # 去掉头部信息，只保留 base64 编码部分
    image_data = base64_string.split(',')[1]

    # 解码 base64 字符串
    decoded_image_data = base64.b64decode(image_data)

    # 使用 BytesIO 将解码后的数据转换为图像对象
    image = Image.open(BytesIO(decoded_image_data))

    # 保存图像到文件
    image.save("output_image.png")

    print("图片已保存为 output_image.png")


from PIL import Image

# 打开 PNG 图片
image = Image.open("./bllose/esign/esignico.png")

# 创建一个空的图像列表
icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
images = []

# 为每个尺寸创建一个缩略图
for size in icon_sizes:
    img = image.resize(size, Image.LANCZOS)
    images.append(img)

# 保存为 ICO 文件
images[3].save("esign.ico", format="ICO", sizes=icon_sizes)