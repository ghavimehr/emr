Dynamic DataTables 
=========================

.. title:: Dynamic DataTables -  Dynamic Django Starter      
.. meta::
    :description: Manage any model without coding using server-side Dynamic DataTables feature via Dynamic Django  
    :keywords: server-side datatables, dynamic datatables, dynamic django, dynamic programming, dynamic patterns

This page explains how the **Dynamic DataTables** feature of `Dynamic Django <./index.html>`__ that allows to manage large amounts of information using a server-side paginated view.   

.. include::  /_templates/components/banner-top.rst

Configuration 
-------------

The `django_dyn_dt`, the application that handles the feature, is registered in the `INSTALLED_APPS` section. 

.. code-block:: python
    :caption: core/settings.py  

    INSTALLED_APPS = [
        ...
        "django_dyn_api",
        ...
    ]

**Dynamic DataTable** section (also covered in the configuration page) provides a simple way to specify the models that are automatically managed. 

The section is a dictionary where the key is the segment of the endpoint and the value the import path of the model. Here are the DEMOs for the default models: 

- `Sales Dynamic Tables View <https://dynamic-django.onrender.com/dynamic-dt/sales/>`__: Demo Link 
- `Product Dynamic Tables View <https://dynamic-django.onrender.com/dynamic-dt/product/>`__: Demo Link 

.. code-block:: python
    :caption: core/settings.py  

    # Syntax: URI -> Import_PATH
    DYNAMIC_DATATB = {
        "product": "home.models.Product",
        "sales": "home.models.Sales",
    }    


Add a new Model  
---------------

Besides the default tables view (Sales and Product models), the Dynamic DataTable feature can be extended to any new model. 
Here are the steps to enable a new endpoint 

- **Define a new model** `Homework` in the `home` aplication

.. code-block:: python
    :caption: home/models.py  

    class Homework(models.Model):
        id = models.AutoField(primary_key=True)
        title = models.CharField(max_length=100)
        content = models.TextField(blank=True, null=True, default='')

- **Migrate the database** 

.. code-block:: bash

    python manage.py makemigrations
    python manage.py migrate    

- **Update the configuration**: `DYNAMIC_API` section 

.. code-block:: python
    :caption: core/settings.py  

    # Syntax: URI -> Import_PATH
    DYNAMIC_DATATB = {
        "product": "home.models.Product",
        "sales": "home.models.Sales",
        "homework": "home.models.Homework",  # <-- NEW 
    }

- **The new view** is now listed in the **Dynamic DataTable** page and ready to be used. 

.. image:: https://github.com/user-attachments/assets/4e2f2739-c34a-4714-865b-33f7da48950d
   :alt: Dynamic DataTable - New view (model) registered 

- **The new DataTable** for the newly created model 

.. image:: https://github.com/user-attachments/assets/a4d4c311-10cb-4682-a9bd-7fa61be3febe
   :alt: Dynamic DataTable - New view for the Homework Model   

Deploy on Render
----------------

This video material explains how to process CSV files and convert them into secure APIs and server-side data tables using **Dynamic Django** tool.

..  youtube:: cXiUsyi_GJs
    :width: 100%

.. include::  /_templates/components/footer-links.rst
