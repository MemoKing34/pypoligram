from .on_business_connection import OnBusinessConnection
from .on_business_message import OnBusinessMessage
from .on_callback_query import OnCallbackQuery
from .on_chat_boost import OnChatBoost
from .on_chat_join_request import OnChatJoinRequest
from .on_chat_member_updated import OnChatMemberUpdated
from .on_chosen_inline_result import OnChosenInlineResult
from .on_connect import OnConnect
from .on_deleted_business_messages import OnDeletedBusinessMessages
from .on_deleted_messages import OnDeletedMessages
from .on_disconnect import OnDisconnect
from .on_edited_business_message import OnEditedBusinessMessage
from .on_edited_message import OnEditedMessage
from .on_error import OnError
from .on_guest_message import OnGuestMessage
from .on_inline_query import OnInlineQuery
from .on_managed_bot import OnManagedBot
from .on_message import OnMessage
from .on_message_reaction import OnMessageReaction
from .on_message_reaction_count import OnMessageReactionCount
from .on_poll import OnPoll
from .on_pre_checkout_query import OnPreCheckoutQuery
from .on_purchased_paid_media import OnPurchasedPaidMedia
from .on_raw_update import OnRawUpdate
from .on_shared_widget_query import OnSharedWidgetQuery
from .on_shipping_query import OnShippingQuery
from .on_start import OnStart
from .on_stop import OnStop
from .on_stopped_message_generation import OnStoppedMessageGeneration
from .on_story import OnStory
from .on_user_status import OnUserStatus
from .on_widget_query import OnWidgetQuery


class Decorators(
	OnBusinessConnection,
	OnBusinessMessage,
	OnCallbackQuery,
	OnChatBoost,
	OnChatJoinRequest,
	OnChatMemberUpdated,
	OnChosenInlineResult,
	OnConnect,
	OnDeletedBusinessMessages,
	OnDeletedMessages,
	OnDisconnect,
	OnEditedBusinessMessage,
	OnEditedMessage,
	OnError,
	OnGuestMessage,
	OnInlineQuery,
	OnManagedBot,
	OnMessage,
	OnMessageReaction,
	OnMessageReactionCount,
	OnPoll,
	OnPreCheckoutQuery,
	OnPurchasedPaidMedia,
	OnRawUpdate,
	OnSharedWidgetQuery,
	OnShippingQuery,
	OnStart,
	OnStop,
	OnStoppedMessageGeneration,
	OnStory,
	OnUserStatus,
	OnWidgetQuery,
):
	pass
