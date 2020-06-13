from django.shortcuts import render, redirect
from . import views
from django.http import HttpResponse, JsonResponse
from .forms import Form_Registration, Form_login
from .models import Regestration, Transaction
from django.contrib import messages

import hashlib
import datetime
import json
import random


# Create your views here.

class Blockchain:
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.data = []
        self.hash = hashlib.sha256(
            str(len(self.chain) + 1).encode()).hexdigest()
        self.create_block()
        table = Regestration.objects.all().exists()
        if table:
            print("yes")
            data = Regestration.objects.all()
            for i in data:

                self.add_data(name=i.name, email=i.email, bitcoin=i.bitcoin,
                              amount=i.amount, m_no=i.m_no, pass1=i.password)
                trans = Transaction.objects.filter(user=i)

                for j in trans:
                    self.transactions.append({
                        'sender': j.sender,
                        'reciver': j.receiver,
                        'amount': j.amount,
                        'bitcoin': j.bitcoin,
                        'time': j.time,
                    })

                self.create_block(i.index, i.timestamp,
                                  i.u_hash, i.nonce, i.u_prev_hash)

    def create_block(
            self,
            index=1,
            timestamp=str(datetime.datetime.now()),
            hash=hashlib.sha256(str(1).encode()).hexdigest(),
            nonce=1,
            previous_hash='0'):

        block = {
            'index': index,
            'timestamp': timestamp,
            'hash': hash,
            'nonce': 500,
            'data': self.data,
            'previous_hash': previous_hash,
            'transaction': self.transactions,
        }
        print('\n\n \t Create Block Call \t \n')
        print(json.dumps(block, indent=4))
        print('\n\n')
        self.data = []
        self.transactions = []
        self.chain.append(block)
        # print(self.chain)
        return block

    def get_last_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_nonce):
        new_nonce = 1
        check_nonce = False
        while check_nonce is False:
            hash_operation = hashlib.sha256(
                str(new_nonce**2-previous_nonce**2).encode()).hexdigest()
            if hash_operation[:4] == "0000":
                print(hash_operation)
                check_nonce = True
            else:
                new_nonce += 1
        return new_nonce

    def add_data(self, name, email, bitcoin=0.0, amount=0, m_no=0, pass1='test'):
        user_data = {
            'Name': name,
            'Email': email,
            'Amount': int(amount),
            'Bitcoin': int(bitcoin),
            'M_no': int(m_no),
            'Passworld': pass1,
        }
        self.data.append(user_data)
        previous_block = self.get_last_block()
        return previous_block['index'] + 1


blockchain = Blockchain()


def Wallet(request):
    print("********************WALLET CALLING***********************")
    if 'user' in request.session:
        data = Regestration.objects.get(u_hash=request.session['user'])
        tot_trans = Transaction.objects.filter(user=data).count()
        trans = Transaction.objects.filter(user=data)

        return render(request, 'Wallet.html', {'data': data, 'tran': trans, 'tot': tot_trans})
    return redirect('login')


def logout(request):
    print("*********************LOGOUT CALLING************************")
    if 'user' in request.session:
        del request.session['user']
        return redirect('login')
    return redirect('login')


def login(request):
    print("*****************LOGIN CALLING************************")
    if request.POST:
        em = request.POST['email']
        ps = request.POST['passworld']
        try:
            valid = Regestration.objects.get(email=em)
            if valid.password == ps:
                if 'admin@gmail.com' == em:
                   
                    request.session['admin'] = valid.u_hash
                    return redirect('Admin_Wallet')
                else:
          
                    request.session['user'] = valid.u_hash
                    print(request.session['user'])
                    return redirect('Wallet')
            else:
                messages.add_message(
                    request, messages.ERROR, "Wrong Passworld.........")
        except:
            messages.add_message(request, messages.ERROR,
                                 "Wrong Email........")
    return render(request, 'login.html')


def Regi(request):
    print("*************************REGI CALLING**********************************")

    if request.POST:
        reg = Regestration()
        reg.name = request.POST['name']
        reg.email = request.POST['email']
        reg.amount = request.POST['amount']
        reg.m_no = request.POST['number']
        reg.password = request.POST['passworld']

        previous_block = blockchain.get_last_block()

        reg.index = int(previous_block['index']) + 1
        reg.u_hash = hashlib.sha256(str(reg.index).encode()).hexdigest()
        previous_nonce = previous_block['nonce']
        reg.nonce = blockchain.proof_of_work(previous_nonce)
        reg.u_prev_hash = previous_block['hash']
        reg.timestamp = str(datetime.datetime.now())

        try:
            print(
                ":::::::::::::::::::::::::::Try block execute:::::::::::::::::::::::::::::")

            valid = Regestration.objects.get(email=request.POST['email'])
            messages.add_message(request, messages.ERROR,
                                 "User already exists")

        except:
            blockchain.add_data(name=reg.name, email=reg.email,amount=reg.amount, m_no=reg.m_no, pass1=reg.password)
            blockchain.create_block(index=reg.index, timestamp=reg.timestamp,hash=reg.u_hash, nonce=reg.nonce, previous_hash=reg.u_prev_hash)
            reg.save()

            return redirect('login')
    return render(request, "regi.html")


def Transact_money(request):
    print("****************Transact_money CALLING******************")
    if 'user' in request.session or 'admin' in request.session:
        if request.POST:
            reciver = request.POST['reciver']
            amount = float(request.POST['amount'])
            send_mess = request.POST['send_note']
            print(reciver)
            print(amount)
            print(send_mess)

            tran_count = 0
            sender_data = Regestration.objects.get(u_hash=request.session['user'])
        

            tran_count = Transaction.objects.filter(user=sender_data).count()

            if reciver == sender_data.u_hash:
                messages.add_message(
                    request, messages.ERROR, "You can't send money to yourself")
                return redirect('Transact_money')

            if float(amount) > float(sender_data.amount):
                messages.add_message(
                    request, messages.ERROR, "You have Not sufficient Balance " + str(sender_data.amount))
                return redirect('Transact_money')

            else:
                if tran_count >= 5:
                    new = ((amount*2)/100)
                    amount = amount-new

                try:
                    reciver_data = Regestration.objects.get(
                        u_hash=str(reciver))

                    print(sender_data.amount)

                    if tran_count >= 5:
                        sender_data.amount -= float(amount+new)

                    else:
                        sender_data.amount -= float(amount)
                    print(sender_data.amount)

                    print(reciver_data.amount)
                    reciver_data.amount += float(amount)
                    print(reciver_data.amount)

                    ######################Transaction Entry In Sender's Block######################
                    blockchain.add_data(
                        name=sender_data.name,
                        email=sender_data.email,
                        amount=sender_data.amount,
                        bitcoin=sender_data.bitcoin,
                        m_no=sender_data.m_no,
                        pass1=sender_data.password
                    )

                    blockchain.transactions.append(
                        {
                            'sender': sender_data.u_hash,
                            'reciver': reciver_data.u_hash,
                            'amount': amount,
                            'bitcoin': 0.0,
                            'time': str(datetime.datetime.now()),
                        }
                    )
                    blockchain.create_block(sender_data.index, sender_data.timestamp,
                                            sender_data.u_hash, sender_data.nonce, sender_data.u_prev_hash)

                    # Transaction Entry in sender's block(to Admin)
                    if tran_count >= 5:
                        admin_user = Regestration.objects.get(
                            email='admin@gmail.com')
                        blockchain.add_data(
                            name=sender_data.name,
                            email=sender_data.email,
                            amount=sender_data.amount,
                            bitcoin=sender_data.bitcoin,
                            m_no=sender_data.m_no,
                            pass1=sender_data.password
                        )

                        blockchain.transactions.append(
                            {
                                'sender': sender_data.u_hash,
                                'reciver': admin_user.u_hash,
                                'amount': new,
                                'bitcoin': 0.0,
                                'time': str(datetime.datetime.now()),
                            }
                        )
                        blockchain.create_block(sender_data.index, sender_data.timestamp,
                                                sender_data.u_hash, sender_data.nonce, sender_data.u_prev_hash)

                        ###################Transaction Entry In Sender's Database (admin)####################
                        tran = Transaction()
                        tran.user = sender_data
                        tran.sender = sender_data.u_hash
                        tran.receiver = admin_user.u_hash
                        tran.amount = new
                        tran.bitcoin = 0.0
                        tran.time = str(datetime.datetime.now())
                        tran.send_notes = send_mess
                        tran.save()

                    ####################Transaction Entry In Reciver's Block######################
                    blockchain.add_data(
                        name=reciver_data.name,
                        email=reciver_data.email,
                        amount=reciver_data.amount,
                        bitcoin=reciver_data.bitcoin,
                        m_no=reciver_data.m_no,
                        pass1=reciver_data.password
                    )
                    blockchain.transactions.append(
                        {
                            'sender': sender_data.u_hash,
                            'reciver': reciver_data.u_hash,
                            'amount': amount,
                            'bitcoin': 0.0,
                            'time': str(datetime.datetime.now())
                        }
                    )
                    blockchain.create_block(reciver_data.index, reciver_data.timestamp,
                                            reciver_data.u_hash, reciver_data.nonce, reciver_data.u_prev_hash)

                    # Transaction entry in Admin side
                    if tran_count >= 5:
                        admin_user = Regestration.objects.get(
                            email='admin@gmail.com')
                        blockchain.add_data(
                            name=admin_user.name,
                            email=admin_user.email,
                            amount=admin_user.amount,
                            bitcoin=admin_user.bitcoin,
                            m_no=admin_user.m_no,
                            pass1=admin_user.password
                        )
                        blockchain.transactions.append(
                            {
                                'sender': sender_data.u_hash,
                                'reciver': admin_user.u_hash,
                                'amount': new,
                                'bitcoin': 0.0,
                                'time': str(datetime.datetime.now())
                            }
                        )
                        blockchain.create_block(
                            admin_user.index, admin_user.timestamp, admin_user.u_hash, admin_user.nonce, admin_user.u_prev_hash)
                        admin_user.amount += new
                        admin_user.save()

                        tran = Transaction()
                        tran.user = reciver_data
                        tran.sender = sender_data.u_hash
                        tran.receiver = reciver_data.u_hash
                        tran.amount = new
                        tran.bitcoin = new
                        tran.time = str(datetime.datetime.now())
                        tran.receive_notes = send_mess
                        tran.save()

                    sender_data.save()
                    reciver_data.save()

                    ###################Transaction Entry In Sender's Database####################

                    tran = Transaction()
                    tran.user = sender_data
                    tran.sender = sender_data.u_hash
                    tran.receiver = reciver_data.u_hash
                    tran.amount = amount
                    tran.bitcoin = 0.0
                    tran.time = str(datetime.datetime.now())
                    tran.send_notes = send_mess
                    tran.save()

                    ##################Transaction Entry In Reciver's Database##################
                    tran = Transaction()
                    tran.user = reciver_data
                    tran.sender = sender_data.u_hash
                    tran.receiver = reciver_data.u_hash
                    tran.amount = amount
                    tran.bitcoin = 0.0
                    tran.time = str(datetime.datetime.now())
                    tran.receive_notes = send_mess
                    tran.save()

                    messages.add_message(
                        request, messages.ERROR, "Money Sent Successfully.......!!!!!!!")
                    return redirect('Transact_money')

                except:
                    messages.add_message(
                        request, messages.ERROR, "No Reciver Exists.......!!!!!!!")
                    return redirect('Transact_money')

        return render(request, 'transact.html')
    return redirect('login')


def Bitcoin(request, id):
    print("***************Bitcoin CALLING*******************")
    if 'user' in request.session:
        User = Regestration.objects.get(id=id)
        new_nonce = 0
        while True:
            ran_val = random.random()
            hash_operation = hashlib.sha256(
                str(ran_val**2 - new_nonce**2).encode()).hexdigest()
            if hash_operation[0:4] == '0000':
                print("Done........!!!")
                User.bitcoin += 0.00014
                User.save()
                break
            else:
                new_nonce += 1
        return redirect('Wallet')
    return redirect('login')


def Transact_bitcoin(request):
    print("****************Transact_bitcoin CALLING*****************")
    if 'user' in request.session:
        if request.POST:
            reciver = request.POST['reciver']
            bitcoin = float(request.POST['amount'])
            send_mess = request.POST['send_note']

            tran_count = 0
            sender_data = Regestration.objects.get(u_hash=request.session['user'])
           
            if float(sender_data.bitcoin) <= 0.00014:
                messages.add_message(
                    request, messages.ERROR, "You Must have more bitcoin then 0.00014" + str(sender_data.bitcoin))

            tran_count = Transaction.objects.filter(user=sender_data).count()
            print(tran_count)

            if reciver == sender_data.u_hash:
                messages.add_message(
                    request, messages.ERROR, "You can't send money to yourself")
                return redirect('Transact_bitcoin')

            if float(bitcoin) > float(sender_data.bitcoin):
                messages.add_message(
                    request, messages.ERROR, "You have Not sufficient Balance " + str(sender_data.bitcoin))
                return redirect('Transact_bitcoin')

            else:
                if tran_count >= 5:
                    new = 0.0001
                    bitcoin = bitcoin-new

                try:
                    reciver_data = Regestration.objects.get(
                        u_hash=str(reciver))

                    print("Sender Bitcoin", sender_data.bitcoin)
                    if tran_count >= 5:
                        sender_data.bitcoin -= float(bitcoin+new)
                    else:
                        sender_data.bitcoin -= float(bitcoin)
                    print("Sender Bitcoin", sender_data.bitcoin)

                    print("Reciver Bitcoin", reciver_data.bitcoin)
                    reciver_data.bitcoin += float(bitcoin)
                    print("Reciver Bitcoin", reciver_data.bitcoin)

                    # Transaction entry in sender databese
                    blockchain.add_data(
                        name=sender_data.name,
                        email=sender_data.email,
                        amount=sender_data.amount,
                        bitcoin=sender_data.bitcoin,
                        m_no=sender_data.m_no,
                        pass1=sender_data.password,
                    )
                    blockchain.transactions.append(
                        {
                            'sender': sender_data.u_hash,
                            'reciver': reciver_data.u_hash,
                            'amount': 0,
                            'bitcoin': bitcoin,
                            'time': str(datetime.datetime.now()),
                        }
                    )
                    blockchain.create_block(sender_data.index, sender_data.timestamp,
                                            sender_data.u_hash, sender_data.nonce, sender_data.u_prev_hash)

                    # Transaction Entry in sender's block(to Admin)
                    if tran_count >= 5:
                        admin_user = Regestration.objects.get(
                            email='admin@gmail.com')
                        blockchain.add_data(
                            name=sender_data.name,
                            email=sender_data.email,
                            amount=sender_data.amount,
                            bitcoin=sender_data.bitcoin,
                            m_no=sender_data.m_no,
                            pass1=sender_data.password
                        )

                        blockchain.transactions.append(
                            {
                                'sender': sender_data.u_hash,
                                'reciver': admin_user.u_hash,
                                'amount': 0,
                                'bitcoin': new,
                                'time': str(datetime.datetime.now()),
                            }
                        )
                        blockchain.create_block(sender_data.index, sender_data.timestamp,
                                                sender_data.u_hash, sender_data.nonce, sender_data.u_prev_hash)

                        ###################Transaction Entry In Sender's Database (admin)####################
                        tran = Transaction()
                        tran.user = sender_data
                        tran.sender = sender_data.u_hash
                        tran.receiver = admin_user.u_hash
                        tran.amount = 0
                        tran.bitcoin = new
                        tran.time = str(datetime.datetime.now())
                        tran.send_notes = send_mess
                        tran.save()

                    # Transaction entry in resiver databese
                    blockchain.add_data(
                        name=reciver_data.name,
                        email=reciver_data.email,
                        amount=reciver_data.amount,
                        bitcoin=reciver_data.bitcoin,
                        m_no=reciver_data.m_no,
                        pass1=reciver_data.password
                    )
                    blockchain.transactions.append(
                        {
                            'sender': sender_data.u_hash,
                            'reciver': reciver_data.u_hash,
                            'amount': 0,
                            'bitcoin': bitcoin,
                            'time': str(datetime.datetime.now())
                        }
                    )
                    blockchain.create_block(reciver_data.index, reciver_data.timestamp,
                                            reciver_data.u_hash, reciver_data.nonce, reciver_data.u_prev_hash)

                    # Transaction entry in Admin side
                    if tran_count >= 5:
                        admin_user = Regestration.objects.get(
                            email='admin@gmail.com')
                        blockchain.add_data(
                            name=admin_user.name,
                            email=admin_user.email,
                            amount=admin_user.amount,
                            bitcoin=admin_user.bitcoin,
                            m_no=admin_user.m_no,
                            pass1=admin_user.password
                        )
                        blockchain.transactions.append(
                            {
                                'sender': sender_data.u_hash,
                                'reciver': admin_user.u_hash,
                                'amount': 0,
                                'bitcoin': new,
                                'time': str(datetime.datetime.now())
                            }
                        )
                        blockchain.create_block(
                            admin_user.index, admin_user.timestamp, admin_user.u_hash, admin_user.nonce, admin_user.u_prev_hash)
                        admin_user.bitcoin += new
                        admin_user.save()

                        tran = Transaction()
                        tran.user = reciver_data
                        tran.sender = sender_data.u_hash
                        tran.receiver = reciver_data.u_hash
                        tran.amount = new
                        tran.bitcoin = new
                        tran.time = str(datetime.datetime.now())
                        tran.receive_notes = send_mess
                        tran.save()

                    sender_data.save()
                    reciver_data.save()

                    ###################Transaction Entry In Sender's Database####################
                    tran = Transaction()
                    tran.user = sender_data
                    tran.sender = sender_data.u_hash
                    tran.receiver = reciver_data.u_hash
                    tran.amount = 0
                    tran.bitcoin = bitcoin
                    tran.time = str(datetime.datetime.now())
                    tran.send_notes = send_mess
                    tran.save()

                    ##################Transaction Entry In Reciver's Database##################
                    tran = Transaction()
                    tran.user = reciver_data
                    tran.sender = sender_data.u_hash
                    tran.receiver = reciver_data.u_hash
                    tran.amount = 0
                    tran.bitcoin = bitcoin
                    tran.time = str(datetime.datetime.now())
                    tran.receive_notes = send_mess
                    tran.save()

                    messages.add_message(
                        request, messages.ERROR, "Bitcoin Sent Successfully.......!!!!!!!")
                    return redirect('Transact_bitcoin')

                except:
                    messages.add_message(
                        request, messages.ERROR, "No Reciver Exists.......!!!!!!!")
                    return redirect('Transact_bitcoin')

        return render(request, 'transact.html')
    return redirect('login')


def Convert(request, id):
    if 'user' in request.session:
        User = Regestration.objects.get(id=id)
        if User.bitcoin < 0.00014:
            return redirect('Wallet')
        else:
            User.amount += User.bitcoin/0.00014
            User.bitcoin = 0.0
            User.save()
            return redirect('Wallet')
    return redirect('login')


def Forgot_Pass(request):
    if request.POST:
        email = request.POST['email']
        number = request.POST['m_no']

        try:
            valid = Regestration.objects.get(email=email)
            if int(valid.m_no) == int(number):
                print(email)
                request.session['useremail'] = email

                numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
                num = ""
                for i in range(4):
                    num += str(random.choice(numbers))

                num = int(num)
                print(num)
                request.session['otp'] = num
                return render(request, "OTP.html", {'otp': num})

            else:
                messages.add_message(
                    request, messages.ERROR, "Mobile Number is not registered.......!!!!!!!")
                return redirect('forgot_pass')

        except:
            messages.add_message(request, messages.ERROR,
                                 "Email Is not Registered.......!!!!!!!")
            return redirect('forgot_pass')

    return render(request, "Forgot_Pass.html")


def Check_OTP(request):
    if request.session.has_key('otp'):
        if request.POST:
            otp = request.POST['otp']
            if int(request.session['otp']) == int(otp):
                del request.session['otp']
                return redirect('New_Password')
            else:
                return HttpResponse("<h2><a href="">You have Entered wrong otp</a></h2>")
        else:
            return redirect('forgot_pass')
    return redirect('login')


def New_Password(request):
    if request.session.has_key('useremail'):
        if request.POST:
            pass_1 = request.POST['pass1']
            pass_2 = request.POST['pass2']
            if pass_1 == pass_2:
                valid = Regestration.objects.get(
                    email=request.session['useremail'])
                valid.password = pass_2
                valid.save()
                del request.session['useremail']

            else:
                messages.add_message(
                    request, messages.ERROR, "Password are not same..!!!!")

        return render(request, "New_Pass.html")
    return redirect('login')


def Admin_Wallet(request):
    if 'admin' in request.session:
        data = Regestration.objects.get(u_hash=request.session['admin'])
        trans = Transaction.objects.filter(user=data)
        tot_trans = Transaction.objects.filter(user=data).count()

        all_Users_count = Regestration.objects.all().count()
        users_trans_count = Transaction.objects.all().count()

        return render(request, 'Admin_Wallet.html', {'data': data, 'trans': trans, 'tot_trans': tot_trans, 'user_count': all_Users_count, 'users_trans_count': users_trans_count})

    return redirect('login')


def All_Users(request):
    if 'admin' in request.session:
        all_Users = Regestration.objects.all()
        return render(request, "show_users.html", {'all_users': all_Users})


def View_User(request, id):
    if 'admin' in request.session:
        User = Regestration.objects.get(id=id)
        if 'admin@gmail.com' == User.email:
            return redirect('Admin_Wallet')
        else:
            trans = Transaction.objects.filter(user=User)
            trans_tot = Transaction.objects.filter(user=User).count()
        return render(request, 'View_User.html', {'data': User, 'trans': trans, 'tot_trans': trans_tot})


def Delete_User(request, id):
    if 'admin' in request.session:
        User = Regestration.objects.get(id=id)
        if 'admin@gmail.com' == User.email:
            return redirect('admin_wallet')
        else:
            User.name = "None"
            User.email = ""
            User.amount = 0.0
            User.bitcoin = 0.0
            User.password = ""
            User.m_no = 0

            trans = Transaction.objects.filter(user=User)
            trans.delete()

            User.save()
            return redirect('Admin_Wallet')

    return redirect('login')


# ---------------------------------------------- Admin --------------------------------------#

def Admin_Convert(request, id):
    if 'admin' in request.session:
        User = Regestration.objects.get(id=id)
        if User.bitcoin < 0.00014:
            return redirect('Wallet')
        else:
            User.amount += User.bitcoin/0.00014
            User.bitcoin = 0.0
            User.save()

            return redirect('Admin_Wallet')

    return redirect('login')


def Admin_Bitcoin(request, id):
    if 'admin' in request.session:
        User = Regestration.objects.get(id=id)
        new_nonce = 0
        while True:
            ran_val = random.random()  # 0 = 0.0000000000001 to 0.9999999999999 = 1
            hash_operation = hashlib.sha256(
                str(ran_val**2 - new_nonce**2).encode()).hexdigest()
            if hash_operation[:4] == "0000":
                print('Done ... !!!')
                User.bitcoin += 0.00014
                User.save()
                break
            else:
                new_nonce += 1
        return redirect('Admin_Wallet')
    return redirect('login')


def Admin_Transact_Money(request):
    if 'admin' in request.session:
        if request.POST:
            reciver = request.POST['reciver']
            amount = float(request.POST['amount'])
            send_mess = request.POST['send_note']
            print(reciver, amount, send_mess)
            tran_count = 0

            sender_data = Regestration.objects.get(
                u_hash=request.session['admin'])

            tran_count = Transaction.objects.filter(user=sender_data).count()
            print(tran_count)

            if reciver == sender_data.u_hash:
                messages.add_message(
                    request, messages.ERROR, "You Can't Send Money To Yourself")
                return redirect('admin_transact_money')

            if float(amount) > float(sender_data.amount):
                messages.add_message(
                    request, messages.ERROR, "You Have Not Sufficient Balance " + str(sender_data.amount)+"₹")
                return redirect('admin_transact_money')
            else:
                # if tran_count >= 5:
                #     new = ((amount * 2)/100)
                #     amount = amount - new

                try:
                    reciver_data = Regestration.objects.get(
                        u_hash=str(reciver))

                    print(sender_data.amount)

                    # if tran_count >= 5:
                    #     sender_data.amount -= float(amount + new)
                    # else:
                    #     sender_data.amount -= float(amount)

                    sender_data.amount -= float(amount)

                    print(sender_data.amount)

                    print(reciver_data.amount)

                    reciver_data.amount += float(amount)

                    print(reciver_data.amount)

                    # TRansaction Entry In Sender's Block
                    blockchain.add_data(name=sender_data.name, email=sender_data.email, amount=sender_data.amount,
                                        bitcoin=sender_data.bitcoin, m_no=sender_data.m_no, pass1=sender_data.password)
                    blockchain.transactions.append({
                        'sender': sender_data.u_hash,
                        'receiver': reciver_data.u_hash,
                        'amount': amount,
                        'bitcoin': 0.0,
                        'time': str(datetime.datetime.now())})
                    blockchain.create_block(sender_data.index, sender_data.timestamp,
                                            sender_data.u_hash, sender_data.nonce, sender_data.u_prev_hash)

                    # Transaction Entery in Sender's Block ( to Admin )
                    # if tran_count >= 5:
                    #     admin_user = Registration.objects.get(email='admin@gmail.com')
                    #     blockchain.add_data(name = sender_data.name, email = sender_data.email, amount= sender_data.amount ,bitcoin= sender_data.bitcoin, m_no=sender_data.m_no, pass1=sender_data.password)
                    #     blockchain.transactions.append({
                    #         'sender':sender_data.u_hash,
                    #         'receiver':admin_user.u_hash,
                    #         'amount':new,
                    #         'bitcoin':0.0,
                    #         'time':str(datetime.datetime.now())})
                    #     blockchain.create_block(sender_data.index,sender_data.timestamp,sender_data.u_hash,sender_data.nonce,sender_data.u_prev_hash)

                    #     # Transaction Entry In Sender's DataBase
                    #     tran = Transactions()
                    #     tran.user = sender_data
                    #     tran.sender = sender_data.u_hash
                    #     tran.receiver = admin_user.u_hash
                    #     tran.amount = new
                    #     tran.bitcoin = 0.0
                    #     tran.time = str(datetime.datetime.now())
                    #     tran.save()

                    # Transaction Entry In Reciver's Block
                    blockchain.add_data(name=reciver_data.name, email=reciver_data.email, amount=reciver_data.amount,
                                        bitcoin=reciver_data.bitcoin, m_no=reciver_data.m_no, pass1=reciver_data.password)
                    blockchain.transactions.append({
                        'sender': sender_data.u_hash,
                        'receiver': reciver_data.u_hash,
                        'amount': amount,
                        'bitcoin': 0.0,
                        'time': str(datetime.datetime.now())})
                    blockchain.create_block(reciver_data.index, reciver_data.timestamp,
                                            reciver_data.u_hash, reciver_data.nonce, reciver_data.u_prev_hash)

                    # Transaction Entery In Admin Side
                    # if tran_count >= 5:
                    #     admin_user = Registration.objects.get(email='admin@gmail.com')
                    #     blockchain.add_data(name = admin_user.name, email = admin_user.email,amount= admin_user.amount,bitcoin= admin_user.bitcoin, m_no=admin_user.m_no, pass1=admin_user.password)
                    #     blockchain.transactions.append({
                    #         'sender':sender_data.u_hash,
                    #         'receiver':admin_user.u_hash,
                    #         'amount':new,
                    #         'bitcoin':0.0,
                    #         'time':str(datetime.datetime.now())})
                    #     blockchain.create_block(admin_user.index,admin_user.timestamp,admin_user.u_hash,admin_user.nonce,admin_user.u_prev_hash)

                    #     admin_user.amount += new
                    #     admin_user.save()

                    #     tran = Transactions()
                    #     tran.user = admin_user
                    #     tran.sender = sender_data.u_hash
                    #     tran.receiver = admin_user.u_hash
                    #     tran.amount = new
                    #     tran.bitcoin = 0.0
                    #     tran.time = str(datetime.datetime.now())
                    #     tran.send_notes = send_mess
                    #     tran.save()

                    sender_data.save()

                    reciver_data.save()

                    # Transaction Entry In Sender's DataBase
                    tran = Transaction()
                    tran.user = sender_data
                    tran.sender = sender_data.u_hash
                    tran.receiver = reciver_data.u_hash
                    tran.amount = amount
                    tran.bitcoin = 0.0
                    tran.time = str(datetime.datetime.now())
                    tran.send_notes = send_mess
                    tran.save()

                    # Transaction Entry In Reciver's DataBase
                    tran = Transaction()
                    tran.user = reciver_data
                    tran.sender = sender_data.u_hash
                    tran.receiver = reciver_data.u_hash
                    tran.amount = amount
                    tran.bitcoin = 0.0
                    tran.time = str(datetime.datetime.now())
                    tran.recive_notes = send_mess
                    tran.save()

                    messages.add_message(
                        request, messages.ERROR, 'Money Sent Successfully...')
                    return redirect('admin_transact_money')
                except:
                    messages.add_message(
                        request, messages.ERROR, 'No Resiver Exists ...')
                    return redirect('admin_transact_money')

        return render(request, 'transact.html')
    return redirect('login')


def Admin_Transact_Bitcoin(request):
    if 'admin' in request.session:
        if request.POST:
            reciver = request.POST['reciver']
            bitcoin = float(request.POST['amount'])
            send_mess = request.POST['send_note']
            tran_count = 0

            sender_data = Regestration.objects.get(
                u_hash=request.session['admin'])
            if float(sender_data.bitcoin) <= 0.00014:
                messages.add_message(request, messages.ERROR, 'You Must Have More Bitcoin Then 0.00014 ' +
                                     ", And You have "+str(sender_data.bitcoin)+" Bitcoin")
                return redirect('admin_transact_bitcoin')

            tran_count = Transaction.objects.filter(user=sender_data).count()
            print(tran_count)

            if reciver == sender_data.u_hash:
                messages.add_message(
                    request, messages.ERROR, "You Can't Send Bitcoin To Yourself")
                return redirect('admin_transact_bitcoin')

            if float(bitcoin) > float(sender_data.bitcoin):
                messages.add_message(
                    request, messages.ERROR, "You Have Not Sufficient Bitcoin " + str(sender_data.bitcoin))
                return redirect('admin_transact_bitcoin')
            else:
                # if tran_count >= 5:
                #     new = 0.0001
                #     bitcoin = bitcoin - new

                try:
                    reciver_data = Regestration.objects.get(
                        u_hash=str(reciver))

                    print("Sender Bitcoin", sender_data.bitcoin)
                    # if tran_count >= 5:
                    #     sender_data.bitcoin -= float(bitcoin + new)
                    # else:
                    #     sender_data.bitcoin -= float(bitcoin)

                    sender_data.bitcoin -= float(bitcoin)

                    print("Sender Bitcoin", sender_data.bitcoin)

                    print('Reciver Bitcoin', reciver_data.bitcoin)
                    reciver_data.bitcoin += float(bitcoin)
                    print('Reciver Bitcoin', reciver_data.bitcoin)

                    # Transaction Enter in Sender's Side
                    blockchain.add_data(name=sender_data.name,
                                        email=sender_data.email,
                                        amount=sender_data.amount,
                                        bitcoin=sender_data.bitcoin,
                                        m_no=sender_data.m_no,
                                        pass1=sender_data.password)
                    blockchain.transactions.append({
                        'sender': sender_data.u_hash,
                        'receiver': reciver_data.u_hash,
                        'amount': 0,
                        'bitcoin': bitcoin,
                        'time': str(datetime.datetime.now())})
                    blockchain.create_block(sender_data.index, sender_data.timestamp,
                                            sender_data.u_hash, sender_data.nonce, sender_data.u_prev_hash)

                    # Transaction Entery in Sender's Block ( to Admin )
                    # if tran_count >= 5:
                    #     admin_user = Registration.objects.get(email='admin@gmail.com')
                    #     blockchain.add_data(name = sender_data.name, email = sender_data.email, amount= sender_data.amount ,bitcoin= sender_data.bitcoin, m_no=sender_data.m_no, pass1=sender_data.password)
                    #     blockchain.transactions.append({
                    #         'sender':sender_data.u_hash,
                    #         'receiver':admin_user.u_hash,
                    #         'amount':0,
                    #         'bitcoin':new,
                    #         'time':str(datetime.datetime.now())})
                    #     blockchain.create_block(sender_data.index,sender_data.timestamp,sender_data.u_hash,sender_data.nonce,sender_data.u_prev_hash)

                    #     # Transaction Entry In Sender's DataBase
                    #     tran = Transactions()
                    #     tran.user = sender_data
                    #     tran.sender = sender_data.u_hash
                    #     tran.receiver = admin_user.u_hash
                    #     tran.amount = 0
                    #     tran.bitcoin = new
                    #     tran.time = str(datetime.datetime.now())
                    #     tran.save()

                    # Transaction Enter in Reciver's Side
                    blockchain.add_data(name=reciver_data.name,
                                        email=reciver_data.email,
                                        amount=reciver_data.amount,
                                        bitcoin=reciver_data.bitcoin,
                                        m_no=reciver_data.m_no,
                                        pass1=reciver_data.password)
                    blockchain.transactions.append({
                        'sender': sender_data.u_hash,
                        'receiver': reciver_data.u_hash,
                        'amount': 0,
                        'bitcoin': bitcoin,
                        'time': str(datetime.datetime.now())})
                    blockchain.create_block(reciver_data.index, reciver_data.timestamp,
                                            reciver_data.u_hash, reciver_data.nonce, reciver_data.u_prev_hash)

                    # Transaction Entery In Admin Side
                    # if tran_count >= 5:
                    #     admin_user = Registration.objects.get(email='admin@gmail.com')
                    #     blockchain.add_data(name = admin_user.name, email = admin_user.email,amount= admin_user.amount,bitcoin= admin_user.bitcoin, m_no=admin_user.m_no, pass1=admin_user.password)
                    #     blockchain.transactions.append({
                    #         'sender':sender_data.u_hash,
                    #         'receiver':admin_user.u_hash,
                    #         'amount':0,
                    #         'bitcoin':new,
                    #         'time':str(datetime.datetime.now())})
                    #     blockchain.create_block(admin_user.index,admin_user.timestamp,admin_user.u_hash,admin_user.nonce,admin_user.u_prev_hash)

                    #     admin_user.bitcoin += new
                    #     admin_user.save()

                    #     tran = Transactions()
                    #     tran.user = admin_user
                    #     tran.sender = sender_data.u_hash
                    #     tran.receiver = admin_user.u_hash
                    #     tran.amount = 0
                    #     tran.bitcoin = new
                    #     tran.time = str(datetime.datetime.now())
                    #     tran.send_notes = send_mess
                    #     tran.save()

                    sender_data.save()
                    reciver_data.save()

                    # Transaction Entry In Sender's DataBase
                    tran = Transaction()
                    tran.user = sender_data
                    tran.sender = sender_data.u_hash
                    tran.receiver = reciver_data.u_hash
                    tran.amount = 0
                    tran.bitcoin = bitcoin
                    tran.time = str(datetime.datetime.now())
                    tran.send_notes = send_mess
                    tran.save()

                    # Transaction Entry In Reciver's DataBase
                    tran = Transaction()
                    tran.user = reciver_data
                    tran.sender = sender_data.u_hash
                    tran.receiver = reciver_data.u_hash
                    tran.amount = 0
                    tran.bitcoin = bitcoin
                    tran.time = str(datetime.datetime.now())
                    tran.recive_notes = send_mess
                    tran.save()

                    messages.add_message(
                        request, messages.ERROR, 'Bitcoin Sent Successfully...')
                    return redirect('admin_transact_bitcoin')
                except:
                    messages.add_message(
                        request, messages.ERROR, 'No Resiver Exists ...')
                    return redirect('admin_transact_bitcoin')

        return render(request, 'transact.html')
    return redirect('login')
