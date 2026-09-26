"""
Report view
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
from views.template_view import get_template
from controllers.order_controller import get_report_highest_spending_users, get_report_best_sellers

def show_highest_spending_users():
    """ Show report of highest spending users """
    highest_spending_users = get_report_highest_spending_users()
    user_rows = [f"<li>Utilisateur {user_id} : {total:.2f} $</li>"
                 for user_id, total in highest_spending_users]
    return get_template(f"<h2>Les plus gros acheteurs</h2><ul>{''.join(user_rows)}</ul>")

def show_best_sellers():
    """ Show report of best selling products """
    best_sellers = get_report_best_sellers()
    product_rows = [f"<li>Article {product_id} : {quantity} vendu(s)</li>"
                    for product_id, quantity in best_sellers]
    if not product_rows:
        product_rows = ["<li>Aucune vente enregistrée.</li>"]
    return get_template(f"<h2>Les articles les plus vendus</h2><ul>{''.join(product_rows)}</ul>")
