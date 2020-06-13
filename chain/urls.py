from django.contrib import admin
from django.urls import path , include 
from .views import Wallet,Regi,login,logout,Transact_money,Bitcoin,Transact_bitcoin,Convert,Forgot_Pass,Check_OTP,New_Password,Admin_Wallet,All_Users,View_User,Delete_User,Admin_Transact_Money,Admin_Transact_Bitcoin,Admin_Bitcoin,Admin_Convert
urlpatterns = [
    path('Wallet/',Wallet,name="Wallet"),
    path('regi/',Regi,name="regi"),
    path('login/',login,name="login"),
    path('logout/',logout,name="logout"),
    path('Transact_money/',Transact_money,name="Transact_money"),
    path('mine_bitcoin/<int:id>',Bitcoin,name='mine_bitcoin'),
    path('Transact_bitcoin/',Transact_bitcoin,name="Transact_bitcoin"),
    path('Convert/<int:id>',Convert,name="Convert"),
    path('forgot_pass/',Forgot_Pass,name="forgot_pass"),
    path('Check_OTP/',Check_OTP, name="Check_OTP"),
    path('New_Password/',New_Password,name="New_Password"),
    path('Admin_Wallet/',Admin_Wallet,name="Admin_Wallet"),
    path('all_users/',All_Users,name="all_users"),
    path('view_user/<int:id>/',View_User,name="view_user"),
    path('delete_user/<int:id>/',Delete_User,name="delete_user"),

        # ------------------ Admin -------------'
    
    path('admin_transact_money/',Admin_Transact_Money,name='admin_transact_money'),
    path('admin_transact_bitcoin/',Admin_Transact_Bitcoin,name='admin_transact_bitcoin'),
    path('admin_mine_bitcoin/<int:id>',Admin_Bitcoin,name='admin_mine_bitcoin'),
    path('admin_convert/<int:id>',Admin_Convert,name='admin_convert'),
]

