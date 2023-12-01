correction_word = 'misunderstood'
un_list = ['order', 'invoice', 'warranty', 'KYC', 'Deals and offers', 'account management', 'prime membership']
list_of_words = [correction_word, '1', '2', '3', 'transaction', 'add gift', 'amazon pay balance', 'bill paid', 'buy', 'cancel', 'cancel membership', 'cash', 'check balance', 'end', 'exchange', 'expensive', 'gift card', 'no', 'order placed', 'payments', 'reason', 'replace', 'return', 'security and login', 'situation', 'something else', 'source account', 'undelivered', 'uphappy', 'wallet', 'yes']
# list_of_words = [correction_word, 'yes', 'no', 'ordered', '1', '2', '3', "return", "undelivered", "exchange", 'reason', 'situation', 'amazon pay balance', 'source account', 'replace', 'end']
returned =   [1, 3, 9, 13]
for i in returned:
    print(list_of_words[i])