from .on_callback_query import OnCallbackQuery
from .on_chat_boost import OnChatBoost
from .on_chat_join_request import OnChatJoinRequest
from .on_chat_member_updated import OnChatMemberUpdated
from .on_chosen_inline_result import OnChosenInlineResult
from .on_deleted_messages import OnDeletedMessages
from .on_disconnect import OnDisconnect
from .on_edited_message import OnEditedMessage
from .on_inline_query import OnInlineQuery
from .on_message import OnMessage
from .on_message_reaction import OnMessageReaction
from .on_message_reaction_count import OnMessageReactionCount
from .on_poll import OnPoll
from .on_pre_checkout_query import OnPreCheckoutQuery
from .on_purchased_paid_media import OnPurchasedPaidMedia
from .on_raw_update import OnRawUpdate
from .on_shipping_query import OnShippingQuery
from .on_story import OnStory
from .on_user_status import OnUserStatus


class Decorators(
	OnCallbackQuery,
	OnChatBoost,
	OnChatJoinRequest,
	OnChatMemberUpdated,
	OnChosenInlineResult,
	OnDeletedMessages,
	OnDisconnect,
	OnEditedMessage,
	OnInlineQuery,
	OnMessage,
	OnMessageReaction,
	OnMessageReactionCount,
	OnPoll,
	OnPreCheckoutQuery,
	OnPurchasedPaidMedia,
	OnRawUpdate,
	OnShippingQuery,
	OnStory,
	OnUserStatus,
):
	pass
