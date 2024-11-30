/** @odoo-module **/

import { loadJS } from "@web/core/assets";
import { WebsiteRoot } from "@website/js/content/website_root";



WebsiteRoot.include({
    custom_events: Object.assign({}, WebsiteRoot.custom_events, {
        'gmap_api_request_market_place': '_onGMapAPIRequestMarketPlace',
        'gmap_api_request' : '_loadGMapAPI'

    }),
    init() {
        this._super(...arguments);
        this.rpc = this.bindService("rpc");
        this.orm = this.bindService("orm");
    },
    async _loadGMapAPI(editableMode, refetch) {

        if (refetch || !this._gmapAPILoading) {
            this._gmapAPILoading = new Promise(async resolve => {
                const key = await this._getGMapAPIKey(refetch);
                let location_let,location_lng;
                let location_dest_lat,location_dest_lng;
                window.odoo_gmap_api_post_load = (async function odoo_gmap_api_post_load() {
                        console.log("odoo_gmap_api_post_load");
                        this.autocomplate_location_id = new google.maps.places.Autocomplete(
                        document.getElementById('location_id'),
                        {
                            types: ['establishment'],
                            componentRestrictions: { country: ['IN'] },
                            fields: ['place_id', 'geometry', 'name'],
                        }
                        );

                        this.autocomplate_location_dest_id = new google.maps.places.Autocomplete(
                        document.getElementById('location_dest_id'),
                        {
                            types: ['establishment'],
                            componentRestrictions: { country: ['IN'] },
                            fields: ['place_id', 'geometry', 'name'],
                        }
                        );

                        this.autocomplate_location_id.addListener('place_changed', () => {
                           var location_place = this.autocomplate_location_id.getPlace();
                           const location_place_coordinates = {
                                    lat : location_place.geometry.location.lat(),
                                    lng : location_place.geometry.location.lng()
                           };
                           this.marker.setPosition(location_place_coordinates);
                           this.marker.setMap(this.map);
                           if (this.marker.getDraggable()) {
                               this.marker.setDraggable(false);
                               this.marker.setDraggable(true);
                           }
                           this.map.setCenter(location_place_coordinates);
                           this.map.setZoom(15);
                           location_let = document.getElementById('location_let');
                           location_lng = document.getElementById('location_lng');

                           location_let.value = location_place_coordinates.lat;
                           location_lng.value = location_place_coordinates.lng;
                        });

                        this.autocomplate_location_dest_id.addListener('place_changed', () => {
                            var location_dest_place = this.autocomplate_location_dest_id.getPlace();
                            const location_dest_place_coordinates = {
                                    lat : location_dest_place.geometry.location.lat(),
                                    lng : location_dest_place.geometry.location.lng()
                           };
                           this.marker.setPosition(location_dest_place_coordinates);
                           this.marker.setMap(this.map);
                           if (this.marker.getDraggable()) {
                               this.marker.setDraggable(false);
                               this.marker.setDraggable(true);
                           }
                           this.map.setCenter(location_dest_place_coordinates);
                           this.map.setZoom(15);

                           location_dest_lat = document.getElementById('location_dest_lat');
                           location_dest_lng = document.getElementById('location_dest_lng');

                           location_dest_lat.value = location_dest_place_coordinates.lat;
                           location_dest_lng.value = location_dest_place_coordinates.lng;
                        });
                }).bind(this);

                if (!key) {
                    if (!editableMode && session.is_admin) {
                        const message = _t("Cannot load google map.");
                        const urlTitle = _t("Check your configuration.");
                        this.notification.add(
                            markup(`<div>
                                <span>${message}</span><br/>
                                <a href="/web#action=website.action_website_configuration">${urlTitle}</a>
                            </div>`),
                            { type: 'warning', sticky: true }
                        );
                    }
                    resolve(false);
                    this._gmapAPILoading = false;
                    return;
                }

                await loadJS(`https://maps.googleapis.com/maps/api/js?v=3.exp&libraries=places&callback=odoo_gmap_api_post_load&key=${encodeURIComponent(key)}`);
                if(navigator.geolocation){
                        navigator.geolocation.getCurrentPosition(
                        (position) => {
                          const pos = {
                            lat: position.coords.latitude,
                            lng: position.coords.longitude,
                          };
                          this.marker.setPosition(pos);
                           this.marker.setMap(this.map);
                           if (this.marker.getDraggable()) {
                               this.marker.setDraggable(false);
                               this.marker.setDraggable(true);
                           }
                           this.map.setCenter(pos);
                           this.map.setZoom(15);
                          });


                }
                this.map = new google.maps.Map(document.getElementById("googleMap"), {
                            center: {lat: -25.363, lng: 131.044 },
                            zoom: 6,
                          });
                const myLatLng = { lat: -25.363, lng: 131.044 };
                this.marker = new google.maps.Marker({
                            position: myLatLng,
                            map: this.map,
                            title: "Hello World!",
                          });
            });
        }
        return this._gmapAPILoading;
    },

    async _onGMapAPIRequestMarketPlace(editableMode, refetch) {
        console.log("async onGMapAPIRequestMarketPlace");

        if (refetch || !this._gmapAPILoadingMarketPlace) {
            this._gmapAPILoadingMarketPlace = new Promise(async resolve => {
                const key = await this._getGMapAPIKey(refetch);
                window.odoo_gmap_api_post_load_market_place = (async function odoo_gmap_api_post_load_market_place() {

                           this.directionmap = new google.maps.Map(document.getElementById("googleMapDirection"), {
                            center: {lat: -25.363, lng: 131.044 },
                            zoom: 6,
                          });
                           let location_let = parseFloat(document.getElementById("location_let").value);
                           let location_lng = parseFloat(document.getElementById("location_lng").value);
                           let location_dest_lat = parseFloat(document.getElementById("location_dest_lat").value);
                           let location_dest_lng = parseFloat(document.getElementById("location_dest_lng").value);
                           let sale_order_id = parseInt(document.getElementById("sale_order_id").value);
                            const originLatLng = { lat: location_let, lng: location_lng };
                            const destLatLng = {lat: location_dest_lat, lng: location_dest_lng}// { lat: -25.363, lng: 131.044 };
                            this.origin_marker = new google.maps.Marker({
                                position: originLatLng,
                                map: this.directionmap,
                                title: "Hello World!",
                                icon : "/transporter/static/src/img/start_location_grey800_18dp.png"
                                    });
                              this.dest_marker = new google.maps.Marker({
                                    position: destLatLng,
                                    map: this.directionmap,
                                    title: "Hello World!",
                              });
                              this.origin_marker.setMap(this.directionmap);
                              this.dest_marker.setMap(this.directionmap);
                              this.directionmap.setCenter(originLatLng);

                              var directionsService = new google.maps.DirectionsService();
                              var directionsRenderer = new google.maps.DirectionsRenderer();
                              var origin_location = new google.maps.LatLng(location_let, location_lng);
                              var destination_location = new google.maps.LatLng(location_dest_lat, location_dest_lng);
                              directionsRenderer.setMap(this.directionmap);
                              var request = {
                                origin: origin_location,
                                destination: destination_location,
                                optimizeWaypoints: true,
                                travelMode: 'DRIVING'
                              }
                              directionsService.route(request, function(response, status) {
                                  if(status == "OK"){
                                    directionsRenderer.setDirections(response);
                                  }
                              })

                }).bind(this);
                if (!key) {
                    if (!editableMode && session.is_admin) {
                        const message = _t("Cannot load google map.");
                        const urlTitle = _t("Check your configuration.");
                        this.notification.add(
                            markup(`<div>
                                <span>${message}</span><br/>
                                <a href="/web#action=website.action_website_configuration">${urlTitle}</a>
                            </div>`),
                            { type: 'warning', sticky: true }
                        );
                    }
                    resolve(false);
                    this._gmapAPILoadingMarketPlace = false;
                    return;
                }
                await loadJS(`https://maps.googleapis.com/maps/api/js?v=3.exp&libraries=places&callback=odoo_gmap_api_post_load_market_place&key=${encodeURIComponent(key)}`);



            });
        }
        return this._gmapAPILoadingMarketPlace;
    },


   handleLocationError: function(browserHasGeolocation, infoWindow, pos) {
          infoWindow.setPosition(pos);
          infoWindow.setContent(
            browserHasGeolocation
              ? "Error: The Geolocation service failed."
              : "Error: Your browser doesn't support geolocation.",
          );
          infoWindow.open(map);
        }


});