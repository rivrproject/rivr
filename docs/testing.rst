Testing
=======

rivr includes a test client which allows you to make requests through views and
middlewares.

.. code:: python

    from rivr.test import Client

    client = Client(view)

    response = client.post('/')
    assert response.status_code == 201

.. automodule:: rivr.test

.. autoclass:: Client

   .. automethod:: get
   .. automethod:: post
   .. automethod:: put
   .. automethod:: delete
   .. automethod:: patch
   .. automethod:: head
