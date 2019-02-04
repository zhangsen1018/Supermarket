from datetime import date

from django import forms
from django.core.validators import RegexValidator
from django_redis import get_redis_connection

from user.models import Users, SpAddress
from market import set_password


# 注册ModelForm的模型类
class RegisterModelForm(forms.ModelForm):
    # 用户手机号
    username = forms.CharField(
        error_messages={
            "required": "手机号必填",
        },
        validators=[
            RegexValidator(r'^1[3-9]\d{9}$', "手机号码格式错误!")
        ]
    )
    # 单独定义一个字段
    # 密码
    password = forms.CharField(max_length=16,
                               min_length=8,
                               error_messages={
                                   'required': '必须填写密码',
                                   'min_length': '密码最小长度必须为8位',
                                   'max_length': '密码最大长度不能超过16位',
                               })
    # 确认密码
    repassword = forms.CharField(max_length=16,
                                 min_length=8,
                                 error_messages={
                                     'required': '必须填写确认密码',
                                     'min_length': '密码最小长度必须为8位',
                                     'max_length': '密码最大长度不能超过16位',
                                 })

    # 验证码
    captcha = forms.CharField(max_length=6,
                              error_messages={
                                  'required': "验证码必须填写"
                              })
    # 用户协议
    agree = forms.BooleanField(error_messages={
        'required': '必须同意用户协议'
    })

    # 模型用的 Users
    class Meta:
        model = Users
        fields = ['username']

        # 提示错误信息
        error_messages = {
            "username": {
                'required': '手机号必须填写',
                'max_length': '手机号长度不能大于11',
            }
        }

    # 验证在数据库中 验证手机号是唯一
    def clean_username(self):  # 验证手机号是否已经被注册
        username = self.cleaned_data.get('username')
        flag = Users.objects.filter(username=username).exists()
        if flag:
            # 在数据库中存在 提示错误
            raise forms.ValidationError("该手机号已经被注册,请重新填写")
        else:
            # 返回单个字段 ,不用返回全部
            return username

    # 验证密码是否一致
    def clean(self):
        # 判断两次密码是否一致
        # 在清洗的数据中的到表单提交的数据,密码和确认密码
        # 获取用户名和密码
        password = self.cleaned_data.get('password')
        repassword = self.cleaned_data.get('repassword')

        # 综合校验 验证码 放在这里最合适,不用考虑先后顺序
        # 验证 用户传入的验证码和redis中的是否一样
        # 用户传入的验证码
        if password and repassword and password != repassword:
            # 在密码和确认密码,并且确认密码和密码不一样的时候,提示错误信息
            raise forms.ValidationError({'repassword': "两次密码不一致!"})

        try:
            captcha = self.cleaned_data.get('captcha')
            username = self.cleaned_data.get('username', '')
            # 获取redis中的
            r = get_redis_connection()
            random_code = r.get(username)  # 在redis里的数据是二进制, 转码
            random_code = random_code.decode('utf-8')
            # 验证两个数据是否一致
            if captcha and captcha != random_code:
                raise forms.ValidationError({"captcha": "验证码输入错误!"})
        except:
            raise forms.ValidationError({"captcha": "验证码输入错误!"})

        # 将用户信息保存到cleaned_data中
        # 返回清洗后的所有数据
        return self.cleaned_data


# 登录ModelForm的模型类
class LoginModelForm(forms.ModelForm):
    # 用户手机号
    username = forms.CharField(
        error_messages={
            "required": "手机号必填",
        },
        validators=[
            RegexValidator(r'^1[3-9]\d{9}$', "手机号码格式错误!")
        ]
    )
    # 单独定义一个字段,密码
    password = forms.CharField(max_length=16,
                               min_length=8,
                               error_messages={
                                   'required': '必须填写密码',
                                   'min_length': '密码最小长度必须为8位',
                                   'max_length': '密码最大长度不能超过16位',
                               })

    # 模型用的 Users
    class Meta:
        model = Users
        # 验证手机号
        fields = ['username', 'password']
        # 提示错误信息
        error_messages = {
            "username": {
                'required': '手机号必须填写',
                'max_length': '手机号长度不能大于11',
            },
            'password': {
                'required': '请填写密码',
            },
        }

    def clean(self):
        # # 验证手机号
        # 从清洗的数据中的得到手机号
        username = self.cleaned_data.get('username')

        try:
            # 如果 清洗的数据中有手机号和数据库的一致
            user = Users.objects.get(username=username)
        except Users.DoesNotExist:
            # 不一致,提示错误
            raise forms.ValidationError({'username': '手机号错误'})

        # 验证密码
        # 空字符串是因为创建的加密方法需要必须传值
        password = self.cleaned_data.get('password', '')
        # 如果 清洗的数据中有密码和数据库的不一致,提示错误信息
        if user.password != set_password(password):
            raise forms.ValidationError({'password': '密码错误'})

        # 返回所有清洗后的数据
        self.cleaned_data['user'] = user
        return self.cleaned_data


# 定义个人资料ModelForm的模型
class MemberModelForm(forms.ModelForm):
    # 用户昵称
    my_name = forms.CharField(max_length=50,
                              min_length=2,
                              error_messages={
                                  'min_length': '用户昵称最小长度必须为2位',
                                  'max_length': '用户昵称最大长度不能超过50位',
                              })
    my_birthday = forms.DateField()
    school = forms.CharField(max_length=50,
                             error_messages={
                                 'max_length': '学校最大长度不能超过50位'
                             })
    my_home = forms.CharField(max_length=50,
                              error_messages={
                                  'max_length': '用户详细地址位置最大长度不能超过50位'
                              })
    address = forms.CharField(max_length=50,
                              error_messages={
                                  'max_length': '用户的故乡最大长度不能超过50位'
                              })
    tel = forms.CharField(error_messages={
        "required": "手机号必填",
    },
        validators=[
            RegexValidator(r'^1[3-9]\d{9}$', "手机号码格式错误!")
        ]
    )

    # 模型用的 Users
    class Meta:
        model = Users
        fields = ['my_name', 'school', 'my_home', 'address', 'tel']
        # 提示错误信息
        error_messages = {
            "my_name": {
                'required': '用户昵称必须填写',
                'max_length': '用户昵称长度不能大于50',
                'min_length': '用户昵称最小长度必须为2位',
            },
            'school': {
                'max_length': '学校最大长度不能超过50位'
            },
            'my_home': {
                'max_length': '用户详细地址位置最大长度不能超过50位'
            },
            'address': {
                'max_length': '用户的故乡最大长度不能超过50位'
            },
            'tel': {
                'required': '手机号必须填写',
                'max_length': '手机号长度不能大于11',
            }
        }


# # 创建一个普通的Form类来验证用户提交的修改信息
# class UserEditForm(forms.Form):
#     my_name = forms.CharField(max_length=50,
#                               min_length=2,
#                               error_messages={
#                                   "required": "用户昵称必填!",
#                                   "max_length": "昵称最大长度为50位!",
#                                   "min_length": "昵称最小长度为2位!",
#                               })
#     my_birthday = forms.CharField(error_messages={
#         "required": "用户生日必填!"
#     })
#     my_home = forms.CharField(error_messages={
#         "required": "用户地址必填!"
#     })
#     address = forms.CharField(error_messages={
#         "required": "用户家乡必填!"
#     })
#     # tel = forms.CharField(error_messages={
#     #                                 "required": "手机号必填!"
#     #                         })
#     school = forms.CharField(error_messages={
#         "required": "学校必填!"
#     })
#     sex = forms.ChoiceField(choices=((1, '男'), (2, '女')))


# 创建一个验证用户重置登录密码的Form验证类
class ResetPassWordForm(forms.Form):
    password = forms.CharField(max_length=16,
                               min_length=8,
                               error_messages={
                                   "required": "密码必须填写!",
                                   "min_length": "密码最少要要8个字符!",
                                   "max_length": "密码最多16个字符!"
                               })
    password1 = forms.CharField(max_length=16,
                                min_length=8,
                                error_messages={
                                    "required": "密码必须填写!",
                                    "min_length": "密码最少要要8个字符!",
                                    "max_length": "密码最多16个字符!",
                                })
    password2 = forms.CharField(max_length=16,
                                min_length=8,
                                error_messages={
                                    "required": "密码必须填写!",
                                    "min_length": "密码最少要要8个字符!",
                                    "max_length": "密码最多16个字符!",
                                })

    """   # 验证旧密码
    def clean_password(self):
        # 接收用户传过来的密码
        password = self.cleaned_data.get('password')
        # 将密码加密
        password = set_password(password)
        flag = Users.objects.filter(password=password).exists()
        # 对结果进行判断
        if not flag:
            # 查询到相关的数据, 抛出异常,提示用户手机号码已经被注册,请输入新的手机号或者前往登录界面
            raise forms.ValidationError('旧密码错误')
        else:
            return password
            """

    # 验证两次新密码是否符合要求
    def clean(self):
        # 获取用户两次输入的密码
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        # 判断两次密码是否一致
        if password1 and password2 and password1 != password2:
            # 密码不一致
            raise forms.ValidationError({"password2": "两次输入的密码不一致!"})
        else:
            return self.cleaned_data

    # 验证旧密码
    def check_password(self, request):
        # 接受session上的id值
        id = request.session.get("id")
        # 到数据库查询用户的密码
        password = Users.objects.get(pk=id).password
        # 判断用户输入的旧密码和数据库的密码是否一致
        if password != set_password(self.cleaned_data.get('password')):
            # 密码不一致
            self.add_error('password', '旧密码错误')
            return False
        else:
            return True

# 添加用户收货地址
class AddressModelForm(forms.ModelForm):
    class Meta:
        model = SpAddress
        fields = ['hcity', 'hproper', 'harea', 'detail', 'username', 'phone', 'isDefault']

        error_messages = {
            "harea": {
                "required": "收货地址必填"
            },
            "detail": {
                "required": "详细地址必填"
            },
            "phone": {
                "required": "手机号码必填"
            },
            "username": {
                "required": "收货人姓名必填"
            },
        }

    def clean(self):
        # 验证当前用户的收货地址的数量,如果超过6个就报错
        user_id = self.data.get('user_id')
        count = SpAddress.objects.filter(user_id=user_id, is_delete=False).count()
        if count >= 6:
            raise forms.ValidationError("收货地址数量不能超过6")

        # 默认收货地址只能有一个, 判断当前添加的是否 isDefault==True,
        # 如果是就讲其他的收货地址都设置为False
        isDefault = self.cleaned_data.get("isDefault")
        if isDefault:
            # 如果是就讲其他的收货地址都设置为False
            SpAddress.objects.filter(user_id=user_id).update(isDefault=False)

        return self.cleaned_data

# 用户地址编辑
class AddressEditModelForm(forms.ModelForm):
    class Meta:
        model = SpAddress
        fields = ['hcity', 'hproper', 'harea', 'detail', 'username', 'phone', 'isDefault']

        error_messages = {
            "harea": {
                "required": "收货地址必填"
            },
            "detail": {
                "required": "详细地址必填"
            },
            "phone": {
                "required": "手机号码必填"
            },
            "username": {
                "required": "收货人姓名必填"
            },
        }

    def clean(self):
        # 验证当前用户的收货地址的数量,如果超过6个就报错
        user_id = self.data.get('user_id')

        # 默认收货地址只能有一个, 判断当前添加的是否 isDefault==True,
        # 如果是就讲其他的收货地址都设置为False
        isDefault = self.cleaned_data.get("isDefault")
        if isDefault:
            # 如果是就讲其他的收货地址都设置为False
            SpAddress.objects.filter(user_id=user_id).update(isDefault=False)

        return self.cleaned_data