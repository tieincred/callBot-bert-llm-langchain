import json
from utils.embedding_calculate import transcript
from utils.node_bert_wlogger import TalkNode
from utils.key_word_list import correction_word

start_node = TalkNode('Start Node')
node2 = TalkNode('Node 2')
node3 = TalkNode('Node 3')
node4 = TalkNode('Node 4')
node5 = TalkNode('Node 5')
node6 = TalkNode('Node 6')
node7 = TalkNode('Node 7')
node8 = TalkNode('Node 8')
node9 = TalkNode('Node 9')

# account management nodes
account_manage = TalkNode('account manage')
login_node = TalkNode('login and security')
payments_node = TalkNode('payments')
gift_node = TalkNode('Gifts')

# gift node
gift_add_node = TalkNode('Add Gift') 
gift_balance_check = TalkNode('Balance Check')
gift_cancel_buy = TalkNode('Gift Transaction')
gift_buy_node = TalkNode('Buy Gift')
gift_cancel_node  = TalkNode('Cancel Gift')

# Invoice nodes
invoice_node = TalkNode('Invoice')
warranty_node = TalkNode('Warranty')
node_undel = TalkNode('Undelivered Order Node')
node_exchange = TalkNode('Exchange Order Node')
end_node = TalkNode('End Node')

# Prime membership 
prime_member_node = TalkNode('Prime member')
prime_member_cancel = TalkNode('prime cancel')
prime_member_upgrade = TalkNode('prime upgrade')
not_happy_node = TalkNode('Unhappy')
expensive_node = TalkNode('Too expensive')


# Set up the relationships between nodes
end_node.set_up([None], ['end'], ['audio21.wav'], end_node=True)
node9.set_up([end_node], ['replace'], ['audio20.wav', 'audio20.wav'])
node8.set_up([node2, end_node], ['yes', 'no'], ['audio2.wav','audio17.wav', 'audio2.wav'])
node7.set_up([node8, node8], ['amazon pay balance','source account'], ['audio10.wav', 'audio14.wav', 'audio10.wav'])
node6.set_up([node7, node9], ['yes', 'replace'], ['audio9.wav', 'audio13.wav', 'audio9.wav'])
node_undel.set_up([end_node], ['situation'], ['audio18.wav', 'audio18.wav'])
node_exchange.set_up([end_node], ['reason'], ['audio19.wav', 'audio19.wav'])
node5.set_up([node6, node_undel, node_exchange], ["return", "undelivered", "exchange"], ['audio8.wav', 'audio16.wav', 'audio15.wav', 'audio8.wav'])
node4.set_up([node5, node3], ['yes', 'no'], ['audio7.wav', 'audio12.wav'])
node3.set_up([node4], ['1', '2', '3'], ['audio4.wav', 'audio5.wav', 'audio6.wav'])
gift_cancel_buy.set_up([node8, node8], ['buy', 'cancel'],['gift_buy.wav', 'gift_cancel.wav'])
gift_node.set_up([node8,node8,gift_cancel_buy], ['add gift', 'check balance', 'Buy or cancel'], ['gift_add.wav', 'check_balance.wav', 'gift_buy_cancel.wav'])
payments_node.set_up([node8, node8], ['wallet', 'cash'], ['payments_wallet.wav', 'payments_cash.wav'])
account_manage.set_up([node8, payments_node, gift_node], ['security and login', 'payments', 'gift card'], ["security.wav","payments.wav","gift.wav"])
warranty_node.set_up([node8, node8], ['yes', 'no'], ['warranty.wav', 'warranty_direction.wav'])
invoice_node.set_up([node8, node8], ['bill paid', 'order placed'], ['bill_paid.wav', 'order_placed.wav'])
not_happy_node.set_up([node8, node8], ['yes', 'no'], ['yes_cancel.wav', 'no_cancel.wav'])
expensive_node.set_up([node8, node8], ['yes', 'no'], ['yes_cancel.wav', 'no_cancel.wav'])
prime_member_cancel.set_up([not_happy_node, expensive_node, node8], ['uphappy', 'expensive', 'something else'], ['unhappy.wav', 'expensive.wav', 'else.wav'])
prime_member_upgrade.set_up([node8, node8], ['yes', 'no'], ['yes_upgrade.wav', 'no_upgrade.wav'])
prime_member_node.set_up([prime_member_cancel, prime_member_upgrade], ['cancel','upgrade'], ['cancel_prime.wav', 'upgrade_prime.wav'])
node2.set_up([node3, invoice_node, warranty_node, node8, node8, account_manage, prime_member_node], ['order', 'invoice', 'warranty', 'KYC', 'Deals and offers', 'account management', 'prime membership'], ['audio3.wav', 'invoice.wav', 'warranty.wav', 'kyc.wav', 'deals.wav', 'account.wav', 'prime.wav'])
node2.classify_current = True
start_node.set_up([node4, node2], ['yes', 'no'], ['audio4.wav','audio2.wav'])



# def collect_categories(node, visited):
#     if node is None or node in visited:
#         return set()
    
#     visited.add(node)
    
#     categories_set = set(node.categories) if node.categories else set()
    
#     for next_node in node.next_nodes:
#         categories_set.update(collect_categories(next_node, visited))
    
#     return categories_set


# def traverse(node, visited, nodes_categories):
#     if node is None or node in visited:
#         return
    
#     nodes_categories[node.node_name] = list(collect_categories(node, visited.copy()))
#     visited.add(node)  # Update visited set after collecting the categories.
    
#     for next_node in node.next_nodes:
#         traverse(next_node, visited.copy(), nodes_categories)


def collect_categories(node, visited):
    if node is None or node in visited:
        return set()

    visited.add(node)
    
    # Remove 'end' from categories if it's present
    categories_set = set(node.categories) - set(['end']) if node.categories else set()
    
    for next_node in node.next_nodes:
        categories_set.update(collect_categories(next_node, visited))
    
    return categories_set

def traverse(node, visited, nodes_categories):
    if node is None or node in visited:
        return
    
    # Use node.node_name as the key instead of a sanitized key
    nodes_categories[node.node_name] = list(collect_categories(node, visited.copy()))
    visited.add(node)  # Update visited set after collecting the categories.
    
    for next_node in node.next_nodes:
        traverse(next_node, visited.copy(), nodes_categories)

def categories_to_json(root):
    nodes_categories = {}
    visited = set()
    traverse(root, visited, nodes_categories)
    return json.dumps(nodes_categories, indent=4)



# Get the JSON representation of nodes and their categories.
json_representation = categories_to_json(start_node)

# Print the JSON representation.
print(json_representation)
