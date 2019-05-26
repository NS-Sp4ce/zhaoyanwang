import requests
from bs4 import BeautifulSoup
from pandas.core.frame import DataFrame
import re


class Graduate:
    def __init__(self, province, category, provinceName):
        self.head = {
            "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKi"
            "t/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36"
        }
        self.data = []
        self.province = province
        self.category = category
        self.provinceName = provinceName

    def get_list_fun(self, url, name):
        """获取提交表单代码"""
        response = requests.get(url, headers=self.head)
        resprovince = response.json()
        with open(name + ".txt", "w") as f:
            for x in resprovince:
                f.write(str(x))
                f.write("\n")

    def get_list(self):
        """
        分别获取省，学科门类，专业编号数据
        写入txt文件
        """
        self.get_list_fun("http://yz.chsi.com.cn/zsml/pages/getSs.jsp",
                          "province")
        self.get_list_fun('http://yz.chsi.com.cn/zsml/pages/getMl.jsp',
                          "category")
        self.get_list_fun('http://yz.chsi.com.cn/zsml/pages/getZy.jsp',
                          'major')

    def get_school_url(self):
        """
        输入省份，
        发送post请求，获取数据
        提取数据
        必填省份，学科门类，专业可选填
        返回学校网址
        """
        url = "https://yz.chsi.com.cn/zsml/queryAction.do"
        data = {
            "ssdm": self.province,
            "yjxkdm": self.category,
        }
        response = requests.post(url, data=data, headers=self.head)
        html = response.text
        reg = re.compile(r'(<tr>.*? </tr>)', re.S)
        content = re.findall(reg, html)
        schools_url = re.findall('<a href="(.*?)" target="_blank">.*?</a>',
                                 str(content))
        return schools_url

    def get_college_data(self, url):
        """返回一个学校所有学院数据"""
        response = requests.get(url, headers=self.head)
        html = response.text
        colleges_url = re.findall(
            '<td class="ch-table-center"><a href="(.*?)" target="_blank">查看</a>',
            html)
        return colleges_url

    def get_final_data(self, url):
        """输出一个学校一个学院一个专业的数据"""
        temp = []
        response = requests.get(url, headers=self.head)
        html = response.text
        soup = BeautifulSoup(html, features='lxml')
        summary = soup.find_all('td', {"class": "zsml-summary"})
        for x in summary:
            temp.append(x.get_text())
        self.data.append(temp)

    def get_schools_data(self):
        """获取所有学校的数据"""
        url = "http://yz.chsi.com.cn"
        schools_url = self.get_school_url()
        amount = len(schools_url)
        i = 0
        for school_url in schools_url:
            i += 1
            url_ = url + school_url
            # 找到一个学校对应所有满足学院网址
            colleges_url = self.get_college_data(url_)
            print("已完成" + self.provinceName + "第" + str(i) + "/" +
                  str(amount) + "个高校爬取")
            #time.sleep(1)
            for college_url in colleges_url:
                _url = url + college_url
                self.get_final_data(_url)

    def get_data_frame(self):
        """将列表形数据转化为数据框格式"""
        data = DataFrame(self.data)
        data.to_csv(self.provinceName + "查询招生信息.csv", encoding="utf_8_sig")


if __name__ == '__main__':
    provinceList = [
        '11', '12', '13', '14', '15', '21', '22', '23', '31', '32', '33', '35',
        '36', '41', '42', '43', '44', '51', '52', '53', '61', '62'
    ]
    provinceNmaeDict = {
        '11': '北京市',
        '12': '天津市',
        '13': '河北省',
        '14': '山西省',
        '15': '内蒙古自治区',
        '21': '辽宁省',
        '22': '吉林省',
        '23': '黑龙江省',
        '31': '上海市',
        '32': '江苏省',
        '33': '浙江省',
        '34': '安徽省',
        '35': '福建省',
        '36': '江西省',
        '37': '山东省',
        '41': '河南省',
        '42': '湖北省',
        '43': '湖南省',
        '44': '广东省',
        '45': '广西壮族自治区',
        '46': '海南省',
        '50': '重庆市',
        '51': '四川省',
        '52': '贵州省',
        '53': '云南省',
        '54': '西藏自治区',
        '61': '陕西省',
        '62': '甘肃省',
        '63': '青海省',
        '64': '宁夏回族自治区',
        '65': '新疆维吾尔自治区',
        '71': '台湾省',
        '81': '香港特别行政区',
        '82': '澳门特别行政区'
    }
    category = "0839" #专业代码
    for i in provinceList:
        province = i
        if province in provinceNmaeDict.keys():
            spyder = Graduate(province, category, provinceNmaeDict[province])
            spyder.get_schools_data()
            spyder.get_data_frame()