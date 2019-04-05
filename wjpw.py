from  tkinter import ttk  #导入内部包
import tkinter as tk
import datetime
import numpy as np
global qu_label

def log(msg):
    logfile=open('log.txt','a')
    dt = datetime.datetime.now().strftime('%b-%d-%Y %H:%M:%S')
    logfile.write(dt+': '+msg+'\n')
    logfile.close()

class DISTRICT:#区类
    def __init__(self,code,name):
        ''' 1：芙蓉区,2：天心区,3，7：岳麓区，新系统只用3,4：开福区
            5：雨花区,6：高新区'''
        self.CODE=code
        self.NAME=name
        self.xiaoxue={}
        self.zhongxue={}
        
class STUDENT:#学生信息表
    def __init__(self,code,name,sex):
        self.code=code#学号
        self.name=name#姓名
        self.sex=sex#性别,0为女，1为男
        self.TYPE=0#人员类型，0：未知,1:提前批（特长生，特色生）
                   #2:提前批（配套入学、单独划片、对口升学）3:志愿批,4:派位批
        self.P_CODE=""#来源小学,来自CS_ASSIGNMENT_PS_INFO表
        self.ID_NUMBER=""#身份证号
        self.SXJ_ID=""#市学籍号
        self.GXJ_ID=""#全国学籍号
        self.PUBLIC_NO=""#公办代码,来自CS_ASSIGNMENT_MS_INFO表
        self.PRIVATE_NO=""#民办代码,来自CS_ASSIGNMENT_MS_INFO表
        self.IDEAL_TYPE=0#志愿类型,0为未选择，1为公办优先，2为民办优先
        self.TQ_TYPE=0#提前批类型,只有TYPE为1时，此字段有意义，否则为0
                      #0表示未选，1为配套入学、2为特长生入学、3为特色生入学、4为直升入学
        self.TQ_PROJECT=""#提前项目,提前项目名称，一般只有特长或特色有内容，
                          #只有TQ_TYPE为非0值时有意义，否则为空
        self.PUBLIC_NO=""#公办代码,来自CS_ASSIGNMENT_MS_INFO表
        self.PRIVATE_NO=""#民办代码,来自CS_ASSIGNMENT_MS_INFO表
        self.PUBLIC_SEQ=0#公办随机号
        self.PRIVATE_SEQ=0#民办随机号
        self.FINAL_NO=""#最终学校代码,来自CS_ASSIGNMENT_MS_INFO表

class XIAOXUE:#小学信息类
    def __init__(self,code,name,district,bynum,tqnum,zynum,pwnum):
        self.code=code#学校编号
        self.name=name#学校名称
        self.district=district#所属区,0:长沙市，1:开福区，2:芙蓉区，3:天心区，4:岳麓区，5:望城区，6:高新区
        self.by_num=bynum#毕业人数
        self.tq_num=tqnum#提前批人数
        self.zy_num=zynum#志愿批人数
        self.pw_num=pwnum#派位批人数
        self.student=[]#学生列表
    def __str__(self):
        return "%s %s %s" % (self.code,self.name,self.district)

class ZHONGXUE:#中学信息表
    def __init__(self,code,name,district,gbnum,mbnum):
        self.code=code#学校编号
        self.name=name#学校名称
        self.district=district#所属区,0:长沙市，1:开福区，2:芙蓉区，3:天心区，4:岳麓区，5:望城区，6:高新区
        self.gb_num=gbnum#公办人数,公办招生人数（提前批+志愿批+派位批）
        self.mb_num=mbnum#民办人数,民办招生人数（志愿批+派位批）
        self.student=[]#学生列表
    def __str__(self):
        return "%s %s %s" % (self.code,self.name,self.district)

class ZHAOSHENGJIHUA:#招生计划信息表
    def __init__(self,p_code,p_name,m_code,m_name,plan_num,tb_num,order_num,pw_num=0):
        self.p_code=p_code#小学编号
        self.p_name=p_name#小学名称
        self.m_code=m_code#中学编号
        self.m_name=m_name#中学名称
        self.plan_num=plan_num#计划招生数,公办招生计划数
        self.tb_num=tb_num#填报人数
        self.order_num=order_num#派位排序,用于派位过程中学校之间的排序，1—3?
        self.pw_num=pw_num#实际派位数,志愿批+派位批

class STUDENT_GROUP:#捆绑信息表
    def __init__(self):
        self.MASTER_CODE=""#主学号
        self.MASTER_PCODE=""#主小学编码
        self.SLAVE_CODE=""#从学号
        self.SLAVE_PCODE=""#从小学编码

class CS_ASSIGNMENT_PW_RESULT:#学生派位结果表
    def __init__(self):
        self.STUDENT_CODE=""#学号
        self.NAME=""#姓名
        self.SEX=0#性别,0为女，1为男
        self.TYPE=0#人员类型,0:未知,1:提前批（特长生，特色生）,
                   #2:提前批（配套入学、单独划片、对口升学）,3:志愿批,4:派位批
        self.P_CODE=""#来源小学,来自CS_ASSIGNMENT_PS_INFO表

class WJPW:#微机派位管理类
    def __init__(self):
        '''dist:按区存储学校（包括小学和中学），读入的学生加入到
            各自小学中，（同时按志愿加入到民办中学中）
           proj:存储招生计划，字典，关键码为小学编号，值为招生计划对象的list
        '''
        self.dist={}
        self.dist[1]=DISTRICT(1,'芙蓉区')
        self.dist[2]=DISTRICT(2,'天心区')
        self.dist[3]=DISTRICT(3,'岳麓区')
        self.dist[4]=DISTRICT(4,'开福区')
        self.dist[5]=DISTRICT(5,'雨花区')
        self.dist[6]=DISTRICT(6,'高新区')

        self.proj={}
        self.pwshunxu=(3,2,1,6,5,4)
        self.pwno=1#当前派位的区排号
        
#        raise Exception("Not implemented~")
    def data_in(self):#导入数据
        self.read_pschool()
        self.read_mschool()
        self.read_student()
        self.read_project()
    def read_pschool(self):
        #读入小学信息
        ps = open("pschool.csv",'r')
        k = ps.readline()
        for k in ps:
            s = k.split(',')
            self.dist[int(s[0][0])].xiaoxue[int(s[0])]=\
                XIAOXUE(int(s[0]),s[1],int(s[0][0]),int(s[2]),int(s[3]),int(s[4]),int(s[5]))
        ps.close()
        log('读入文件pschool.csv')
        
    def read_mschool(self):
        #读入中学信息
        ms = open("mschool.csv",'r')
        k = ms.readline()
        for k in ms:
            s = k.split(',')
            self.dist[int(s[0][0])].zhongxue[int(s[0])]=\
                ZHONGXUE(int(s[0]),s[1],int(s[0][0]),int(s[2]),int(s[3]))
        ms.close()
    def read_student(self):
        '''读入所有学生信息，按区按学校分入每一所小学，
           同时如果填报了民办志愿，加入到对应民办学校的集合中，
           集合使用list，一个对象加入多个集合是否会复制或者都是引用？需要测试'''
        st = open('student_pw.csv','r')
        k = st.readline()
        for k in st:
            s = k.split(',')
            qu=int(s[0][0])#区编号
            xx=int(s[0][0:3])#小学编号
            self.dist[qu].xiaoxue[xx].student.append(\
                STUDENT(s[0],s[1],s[2]))
        st.close()
    def read_project(self):
        '''读入学位分配计划'''
        pr=open('project.csv','r')
        k=pr.readline()
        for k in pr:
            k=k.split(',')
            if int(k[0]) not in self.proj:
                self.proj[int(k[0])]=[]
            self.proj[int(k[0])].insert(int(k[1])-1,\
                ZHAOSHENGJIHUA(int(k[0]),k[3],int(k[2]),k[4],int(k[5]),int(k[6]),int(k[1])))
            
                          
    def data_check(self):#数据校验
        raise Exception("Not implemented~")
    def shi_pw(self):#长沙市派位
        raise Exception("Not implemented~")
    def qu_pw(self):#区派位
        global qu_label
        quno=self.pwshunxu[self.pwno]
        qu=self.dist[quno]
#        for xx in qu.xiaoxue:
#            label["text"]="My name is Ben"
#        raise Exception("Not implemented~")
    def gb_pw(self):#公办学校派位
        raise Exception("Not implemented~")
    def mb_pw(self):#民办学校派位
        raise Exception("Not implemented~")
    def data_out(self):#导出数据
        raise Exception("Not implemented~")

def gen_random(n):
    return np.random.randint(10000000,99999999,n)
    
def main():
    print(gen_random(10))
    wjpw=WJPW()
    wjpw.data_in()
    '''
    for k in wjpw.dist:
        for s in wjpw.dist[k].xiaoxue:
            print(wjpw.dist[k].xiaoxue[s])
    '''

#class UI(
def start():
    global qu_label
    ldatain.config(text='数据读入完毕')
    top1=tk.Toplevel()
    w=root.winfo_screenwidth()
    h=root.winfo_screenheight()
    top1.geometry('%dx%d+0+0' % (w,h))#设置窗口大小和位置
    top1.overrideredirect(True)#设置无标题行无边框
    title=['1','2','3','4','5',]
    box = ttk.Treeview(top1,height=30,columns=title, show='headings')#,font=('宋体','20'))
#    box.NodeFont = new Font("Arial", 20, FontStyle.Bold )#;//字体
    box.column('1',width=80,anchor='center')
    box.column('2',width=80,anchor='center')
    box.column('3',width=20,anchor='center')
    box.column('4',width=100,anchor='center')
    box.column('5',width=200,anchor='center')

    box.heading('1',text='考生编号')
    box.heading('2',text='姓  名')
    box.heading('3',text='性别')
    box.heading('4',text='随机号')
    box.heading('5',text='派位结果')
#    for i in range(200):
#        box.insert("",'end',values=("%8d"%(i),"赵钱孙李","男","44444444","我要上麻省理工学院")) #插入数据，
#    box.place(relx=0.5, rely=0.5, anchor=CENTER)
    box.pack(side='left', fill='both')

    vbar = ttk.Scrollbar(top1,orient='vertical',command=box.yview)
    box.configure(yscrollcommand=vbar.set)
    box.grid(row=0,column=0,sticky='NSEW')
    vbar.grid(row=0,column=1,sticky='NS')

    for i in range(20):
        top1.after(10,box.yview_moveto(i/20),top1.update())
    qu_label = tk.Label(top1, text='开福区公办小学')
    qu_label.place(x=550, y=10, anchor='nw')
    xx_label = tk.Label(top1, text='国防科大附小')
    xx_label.place(x=550, y=50, anchor='nw')
    info_label = tk.Label(top1,text='info')
    info_label.place(x=550, y=100, anchor='nw')
    st_button = tk.Button(top1, text='开始', width=20, command=startpw)
    top1.mainloop()

def startpw():
    global qu_label
    qu_label['text']='芙蓉区'
    wjpw.qu_pw()

root=tk.Tk()
root.resizable(0,0)
root.geometry("800x600") #设置窗口大小
#获取显示器大小
w=root.winfo_screenwidth()
h=root.winfo_screenheight()
plc='+%d+%d' % ((w-800)//2,(h-600)//2)
root.geometry(plc)#设置窗口位置，屏幕左上角(100,50)的位置
ldatain=tk.Label(root,bg='red',text='读入数据...',height=4,font=(16),anchor='w')
ldatain.pack(side='left')
wjpw=WJPW()
wjpw.data_in()
#ldatain.config(text='数据读入完毕')
start=tk.Button(root,text='start1',command=start)
start.pack()
'''
b1=tk.Button(root,text='start1',command=show1)
b1.pack()
b2=tk.Button(root,text='start2',command=showMessage)
#b2=tk.Button(root,text='start2',command=show2)
b2.pack()
'''
root.mainloop()


