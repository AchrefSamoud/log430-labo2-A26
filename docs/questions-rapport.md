# Labo 02 — Questions 1 à 5

## Question 1 — Déclenchement de la synchronisation

Initialement, `show_main_menu()` déclenchait la synchronisation à chaque visite de l’accueil. Désormais, `store_manager.py` l’appelle une seule fois au démarrage, avant de lancer le serveur :

```python
if __name__ == "__main__":
    populate_redis_from_mysql()
    server = HTTPServer(("0.0.0.0", 5000), StoreManager)
    server.serve_forever()
```

`populate_redis_from_mysql()` appelle `sync_all_orders_to_redis()`, qui ne lit MySQL que si Redis ne contient aucune clé `order:*`.

## Question 2 — Lecture dans Redis

Dans `queries/read_order.py`, `scan_iter()` repère les commandes et `hgetall()` lit les champs de chacune. Les clés sont triées par identifiant décroissant avant d’appliquer la limite :

```python
order_keys = sorted(
    r.scan_iter(match="order:*"),
    key=lambda key: int(key.split(":", 1)[1]),
    reverse=True,
)[:limit]
for key in order_keys:
    data = r.hgetall(key)
```

## Question 3 — Ajout dans Redis

Après `session.commit()` dans `commands/write_order.py`, `add_order_to_redis()` utilise `hset()` dans un pipeline Redis pour enregistrer la commande :

```python
pipe.hset(f"order:{order_id}", mapping={
    "id": order_id,
    "user_id": user_id,
    "total_amount": total_amount,
})
```

## Question 4 — Suppression dans Redis

Après la suppression confirmée dans MySQL, `delete_order_from_redis()` utilise `delete()` dans le pipeline Redis pour effacer la même clé :

```python
pipe.delete(f"order:{order_id}")
```

## Question 5 — Données nécessaires aux produits les plus vendus

Avant l’activité 6, non : les commandes dans Redis ne contenaient que `id`, `user_id` et `total_amount`. Il fallait consulter les `order_items` dans MySQL ou conserver les quantités vendues par produit dans Redis. L’activité 6 utilise maintenant :

```python
for item in items:
    pipe.incr(f"product:{item['product_id']}", item["quantity"])
```

Au démarrage, les `order_items` historiques alimentent aussi ces compteurs une seule fois.
