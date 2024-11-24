/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { loadJS } from "@web/core/assets";
import { useService } from "@web/core/utils/hooks";
import { createElement } from "@web/core/utils/xml";
console.log("LOADED");
publicWidget.registry.TrnasportWebsite = publicWidget.Widget.extend({
    selector: '.oe_website_map',
    events: {
        'change .oe_website_category_id': '_onChangeCategory'
    },

});

export default publicWidget.registry.TrnasportWebsite;