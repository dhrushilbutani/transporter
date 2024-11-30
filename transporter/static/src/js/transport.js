/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { loadJS } from "@web/core/assets";




publicWidget.registry.Transporter = publicWidget.Widget.extend({
    selector: '.create_order_transport',
    start: async function () {
        this._gmapLoaded = await new Promise(resolve => {
            this.trigger_up('gmap_api_request', {
                editableMode: true,
                configureIfNecessary: true,
                onSuccess: key => {
                },
            });
        });

    },

});

publicWidget.registry.WebsiteDirection = publicWidget.Widget.extend({
    selector: '.o_market_place_form',
    start: async function () {
        this._gmapLoaded = await new Promise(resolve => {
            this.trigger_up('gmap_api_request_market_place', {
                editableMode: true,
                configureIfNecessary: true,
                onSuccess: key => {
                },
            });
        });

    },

});

export default publicWidget.registry.Transporter;
export default publicWidget.registry.WebsiteDirection;
