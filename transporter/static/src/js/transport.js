/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { loadJS } from "@web/core/assets";

publicWidget.registry.Transporter = publicWidget.Widget.extend({
    selector: '.create_order_transport',
    start: async function () {
        await this._super(...arguments);
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
    events: {
        'click .o_payment_submit_transporter': '_onClickPaymentButton',
    },
    init() {
        this._super(...arguments);
        this.orm = this.bindService("orm");
        this.notification = this.bindService("notification");
    },
    start: async function () {
        await loadJS("https://checkout.razorpay.com/v1/checkout.js");

        this._gmapLoadedmarketplace = await new Promise(resolve => {
            this.trigger_up('gmap_api_request_market_place', {
                editableMode: true,
                configureIfNecessary: true,
                onSuccess: key => {
                },
            });
        });

    },
    _onClickPaymentButton: async function(ev){
        const sale_order_id = ev.target.dataset.saleOrderId;
        const res = await this.orm.call("sale.order", "create_order_razor_pay", [parseInt(sale_order_id)])
        if(res.status !== 200){
            this.notification.add(
                        res.error,
                        {
                            type: "danger",
                        }
                    );
        }
        const api_key = res.key_id;
        const order_id = res.order_id;
        var self = this;
        var options = {
                    "key": api_key, // Enter the Key ID generated from the Dashboard
                    "amount": res.amount_total, // Amount is in currency subunits. Default currency is INR. Hence, 50000 refers to 50000 paise
                    "currency": res.currency,
                    "name": res.p,
                    "description": res.description,
                    "image": res.image,
                    "order_id": res.order_od,
                    "callback_url": res.callback_url,
                    "prefill": {
                        "name": res.prefill.name,
                        "email": res.prefill.email,
                        "contact": res.prefill.contact
                    },
                    "handler": async function (response)  {
                        await self.orm.call("sale.order", "payment_done", [parseInt(sale_order_id), response.razorpay_payment_id,])

                        self.notification.add(
                            "Payment Successful Please Refresh Page",
                            { type: 'warning', sticky: false }
                        );

                        },
                    "notes": {
                        "address": res.notes.address
                    },
                    "theme": {
                        "color": res.theme.color,
                    }
                };
        var rzp1 = new Razorpay(options);
        rzp1.on('payment.failed', function (response){
               self.notification.add(
                            response.error.description + ': ' + response.error.reason,
                            { type: 'warning', sticky: false }
                        );
        });
        rzp1.open();

        ev.preventDefault();

    },
});

publicWidget.registry.ShareLiveLocation = publicWidget.Widget.extend({
    selector: '.o_share_live_location',
    events: {
//        'click button.o_assign_vechile_share_location': '_onClickShareLiveLocation',
    },
    start: async function () {
        console.log(">>>>>>>ShareLiveLocation");
        this.rpc = this.bindService("rpc");
    },



});



publicWidget.registry.LanguageSelector = publicWidget.Widget.extend({
    selector: '.google_translate_element',
    start: async function () {
        await this._super(...arguments);
        this._googleTrnsalater = await new Promise(resolve => {
            this.trigger_up('google_language_added', {
                editableMode: true,
                configureIfNecessary: true,
                onSuccess: key => {
                },
            });
        });

    },


//    window.googleTranslateElementInit = (async function googleTranslateElementInit() {
//               console.log(">>>>>>>googleTranslateElementInit");
//            await new google.translate.TranslateElement(
//                {pageLanguage: 'en'},
//                'google_translate_element'
//            );
//
//    }).bind(this);
});

export default publicWidget.registry.Transporter;
export default publicWidget.registry.WebsiteDirection;
export default publicWidget.registry.ShareLiveLocation;
export default publicWidget.registry.LanguageSelector;