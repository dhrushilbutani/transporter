from odoo import models
class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _notify_thread(self, message, msg_vals=False, **kwargs):
        """ Main notification method. This method basically does two things

         * call ``_notify_get_recipients`` that computes recipients to
           notify based on message record or message creation values if given
           (to optimize performance if we already have data computed);
         * performs the notification process by calling the various notification
           methods implemented;

        :param record message: <mail.message> record being notified. May be
          void as 'msg_vals' superseeds it;
        :param dict msg_vals: values dict used to create the message, allows to
          skip message usage and spare some queries;

        Kwargs allow to pass various parameters that are given to sub notification
        methods. See those methods for more details about supported parameters.
        Specific kwargs used in this method:

          * ``scheduled_date``: delay notification sending if set in the future.
            This is done using the ``mail.message.schedule`` intermediate model;

        :return: recipients data (see ``MailThread._notify_get_recipients()``)
        """
        # add lang to context immediately since it will be useful in various rendering later
        self = self._fallback_lang()
        self._raise_for_invalid_parameters(
            set(kwargs.keys()),
            restricting_names=self._get_notify_valid_parameters()
        )

        msg_vals = msg_vals if msg_vals else {}
        recipients_data = self._notify_get_recipients(message, msg_vals, **kwargs)
        if not recipients_data:
            return recipients_data

        # if scheduled for later: add in queue instead of generating notifications
        scheduled_date = self._is_notification_scheduled(kwargs.pop('scheduled_date', None))
        if scheduled_date:
            # send the message notifications at the scheduled date
            self.env['mail.message.schedule'].sudo().create({
                'scheduled_datetime': scheduled_date,
                'mail_message_id': message.id,
                'notification_parameters': json.dumps(kwargs),
            })
        else:
            # generate immediately the <mail.notification>
            # and send the <mail.mail>, <mail.push> and the <bus.bus> notifications
            self.sudo()._notify_thread_by_inbox(message, recipients_data, msg_vals=msg_vals, **kwargs)
            self.sudo()._notify_thread_by_email(message, recipients_data, msg_vals=msg_vals, **kwargs)
            self.sudo()._notify_thread_by_web_push(message, recipients_data, msg_vals, **kwargs)

        return recipients_data