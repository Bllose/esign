from enum import IntEnum

class FileStatus(IntEnum):
    NOT_UPLOADED = 0, "文件未上传"
    UPLOADING = 1, "文件上传中"
    UPLOADED_OR_CONVERTED_HTML = 2, "文件上传已完成 或 文件已转换（HTML）"
    UPLOAD_FAILED = 3, "文件上传失败"
    WAITING_FOR_PDF_CONVERSION = 4, "文件等待转换（PDF）"
    CONVERTED_PDF = 5, "文件已转换（PDF）"
    ADDING_WATERMARK = 6, "加水印中"
    WATERMARK_ADDED = 7, "加水印完毕"
    PDF_CONVERSION_IN_PROGRESS = 8, "文件转化中（PDF）"
    PDF_CONVERSION_FAILED = 9, "文件转换失败（PDF）"
    WAITING_FOR_HTML_CONVERSION = 10, "文件等待转换（HTML）"
    HTML_CONVERSION_IN_PROGRESS = 11, "文件转换中（HTML）"
    HTML_CONVERSION_FAILED = 12, "文件转换失败（HTML）"

    def __new__(cls, value, msg):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.msg = msg
        return obj

    @classmethod
    def from_code(cls, code):
        for member in cls:
            if member.value == code:
                return member
        raise ValueError(f"Invalid code: {code}")

# 示例使用
def get_status_message(code):
    try:
        status = FileStatus.from_code(code)
        return status.msg
    except ValueError as e:
        return str(e)

if __name__ == '__main__':
    # 测试
    print(get_status_message(1))  # 输出: 文件上传中
    print(get_status_message(2))  # 输出: 文件上传已完成 或 文件已转换（HTML）
    print(get_status_message(13)) # 输出: Invalid code: 13