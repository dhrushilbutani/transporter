/** @odoo-module **/

import "@website/snippets/s_website_form/000";  // force deps
import publicWidget from '@web/legacy/js/public/public_widget';
import { session } from "@web/session";
import { debounce } from "@web/core/utils/timing";
const { DateTime } = luxon;
import wUtils from '@website/js/utils';


publicWidget.registry.s_website_form.include({
        start: function () {
            // Reset the form first, as it is still filled when coming back
            // after a redirect.
            this.resetForm();

            // Prepare visibility data and update field visibilities
            const visibilityFunctionsByFieldName = new Map();
            for (const fieldEl of this.el.querySelectorAll('[data-visibility-dependency]')) {
                const inputName = fieldEl.querySelector('.s_website_form_input').name;
                if (!visibilityFunctionsByFieldName.has(inputName)) {
                    visibilityFunctionsByFieldName.set(inputName, []);
                }
                const func = this._buildVisibilityFunction(fieldEl);
                visibilityFunctionsByFieldName.get(inputName).push(func);
                this._visibilityFunctionByFieldEl.set(fieldEl, func);
            }
            for (const [name, funcs] of visibilityFunctionsByFieldName.entries()) {
                this._visibilityFunctionByFieldName.set(name, () => funcs.some(func => func()));
            }

            this._onFieldInputDebounced = debounce(this._onFieldInput.bind(this), 400);
            this.$el.on('input.s_website_form', '.s_website_form_field', this._onFieldInputDebounced);

            this.$allDates = this.$el.find('.s_website_form_datetime, .o_website_form_datetime, .s_website_form_date, .o_website_form_date');
            for (const field of this.$allDates) {
                const input = field.querySelector("input");
                const defaultValue = input.getAttribute("value");
                this.call("datetime_picker", "create", {
                    target: input,
                    onChange: () => input.dispatchEvent(new Event("input", { bubbles: true })),
                    pickerProps: {
                        type: field.matches('.s_website_form_date, .o_website_form_date') ? 'date' : 'datetime',
                        value: defaultValue && DateTime.fromSeconds(parseInt(defaultValue)),
                    },
                }).enable();
            }
            this.$allDates.addClass('s_website_form_datepicker_initialized');

            // Display form values from tag having data-for attribute
            // It's necessary to handle field values generated on server-side
            // Because, using t-att- inside form make it non-editable
            // Data-fill-with attribute is given during registry and is used by
            // to know which user data should be used to prfill fields.
            let dataForValues = wUtils.getParsedDataFor(this.el.id, document);
            debugger;
            if(this._getContext(true)){
                this.editTranslations = !!this._getContext(true).edit_translations;
            }

            // On the "edit_translations" mode, a <span/> with a translated term
            // will replace the attribute value, leading to some inconsistencies
            // (setting again the <span> on the attributes after the editor's
            // cleanup, setting wrong values on the attributes after translating
            // default values...)
            if (!this.editTranslations
                    && (dataForValues || Object.keys(this.preFillValues).length)) {
                dataForValues = dataForValues || {};
                const fieldNames = this.$target.serializeArray().map(el => el.name);
                // All types of inputs do not have a value property (eg:hidden),
                // for these inputs any function that is supposed to put a value
                // property actually puts a HTML value attribute. Because of
                // this, we have to clean up these values at destroy or else the
                // data loaded here could become default values. We could set
                // the values to submit() for these fields but this could break
                // customizations that use the current behavior as a feature.
                for (const name of fieldNames) {
                    const fieldEl = this.el.querySelector(`[name="${CSS.escape(name)}"]`);

                    // In general, we want the data-for and prefill values to
                    // take priority over set default values. The 'email_to'
                    // field is however treated as an exception at the moment
                    // so that values set by users are always used.
                    if (name === 'email_to' && fieldEl.value
                            // The following value is the default value that
                            // is set if the form is edited in any way. (see the
                            // @website/js/form_editor_registry module in editor
                            // assets bundle).
                            // TODO that value should probably never be forced
                            // unless explicitely manipulated by the user or on
                            // custom form addition but that seems risky to
                            // change as a stable fix.
                            && fieldEl.value !== 'info@yourcompany.example.com') {
                        continue;
                    }

                    let newValue;
                    if (dataForValues && dataForValues[name]) {
                        newValue = dataForValues[name];
                    } else if (this.preFillValues[fieldEl.dataset.fillWith]) {
                        newValue = this.preFillValues[fieldEl.dataset.fillWith];
                    }
                    if (newValue) {
                        this.initialValues.set(fieldEl, fieldEl.getAttribute('value'));
                        fieldEl.value = newValue;
                    }
                }
            }
            this._updateFieldsVisibility();

            if (session.geoip_phone_code) {
                this.el.querySelectorAll('input[type="tel"]').forEach(telField => {
                    if (!telField.value) {
                        telField.value = '+' + session.geoip_phone_code;
                    }
                });
            }
            // Check disabled states
            this.inputEls = this.el.querySelectorAll('.s_website_form_field.s_website_form_field_hidden_if .s_website_form_input');
            this._disabledStates = new Map();
            for (const inputEl of this.inputEls) {
                this._disabledStates[inputEl] = inputEl.disabled;
            }

            // Add the files zones where the file blocks will be displayed.
            this.el.querySelectorAll("input[type=file]").forEach(inputEl => {
                const filesZoneEl = document.createElement("DIV");
                filesZoneEl.classList.add("o_files_zone", "row", "gx-1");
                inputEl.parentNode.insertBefore(filesZoneEl, inputEl);
            });

//            return this._super(...arguments).then(() => this.__startResolve());
        },
});

