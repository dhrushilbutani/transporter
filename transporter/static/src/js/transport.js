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
        'click button.o_direction_button' : '_onClickGetDirection',
        'input input[id="customer_input"]': '_onChangeCustomerInput',
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
    _onChangeCustomerInput: function(ev){
            const customer_input = ev.target.value;
            if(customer_input === null || customer_input === undefined){
                document.getElementById("price_table").style.display = "none";
            }
            else{
            document.getElementById("user_amount").innerHTML = parseFloat(customer_input) || 0.00;
            document.getElementById("total_amount").innerHTML = (parseFloat(customer_input) || 0.00) + 50.00;
            document.getElementById("price_table").style.display = "block";
            }


    },

    _onClickGetDirection: function(ev){
            const lat = ev.target.dataset.lat;
            const lng = ev.target.dataset.lng;
            window.open(`https://www.google.com/maps/dir/?api=1&destination=${lat},${lng}&travelmode=driving`);
            ev.preventDefault();
    }
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
});

publicWidget.registry.EditOrder = publicWidget.Widget.extend({
    selector: '.o_edit_order',
    events: {
        'click .o_payment_submit_transporter': '_onClickPaymentButton',
        'input input[id="customer_input"]': '_onChangeCustomerInput',
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
    _onChangeCustomerInput: function(ev){

            const customer_input = ev.target.value;
            if(customer_input === null || customer_input === undefined){
                document.getElementById("price_table").style.display = "none";
            }
            else{
            document.getElementById("user_amount").innerHTML = parseFloat(customer_input) || 0.00;
            document.getElementById("total_amount").innerHTML = (parseFloat(customer_input) || 0.00) + 50.00;
            document.getElementById("price_table").style.display = "block";
            }


    },
});

publicWidget.registry.HomePage = publicWidget.Widget.extend({
    selector: '.o_home_page',
    events: {
        'click .o_learn_more_button': '_onClickLearnMore',

    },
    _onClickLearnMore: function(){
            document.getElementById('connect').scrollIntoView();
    },
});


export default publicWidget.registry.Transporter;
export default publicWidget.registry.WebsiteDirection;
export default publicWidget.registry.ShareLiveLocation;
export default publicWidget.registry.LanguageSelector;