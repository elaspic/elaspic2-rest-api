def firestore_example():
    from google.cloud import firestore

    # Add a new document
    db = firestore.Client()
    doc_ref = db.collection("jobs").document("alovelace")
    doc_ref.set({"first": "Ada", "last": "Lovelace", "born": 1815})

    # Then query for documents
    users_ref = db.collection("users")

    for doc in users_ref.stream():
        print("{} => {}".format(doc.id, doc.to_dict()))
