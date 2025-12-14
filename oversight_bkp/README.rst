.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

=========
Oversight
=========

This module extends the functionality of Odoo to allows users to oversight
servers, configuration, etc.



Configuration
=============

TODO


Road map / Know Issues
======================

* write a doc, to mention how to create users with restricted access on
  distant servers.
* when migrating this module in v10, depends on the module web_auto_fresh.
  For the time being, you can install the Firefox module Reloadmatic.
  https://addons.mozilla.org/fr/firefox/addon/reloadmatic/

New Probes
----------

* 'ssl.certificate' : check if the certificate is correct.
* 'ftp' : Check if FTP service is UP.

New Probes with call to external services
-----------------------------------------

* 'whois' : check if a domain will expire in a short while.
* Call extra check. Ask to QD.

Credits
=======

Contributors
------------

* Sylvain LE GAL (https://www.twitter.com/legalsylvain)

Funders
-------

The development of this module has been financially supported by:

* GRAP, Groupement Régional Alimentaire de Proximité (http://www.grap.coop)
