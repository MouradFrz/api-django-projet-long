import json

from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    users_list = []

    async def connect(self):
        self.cours = self.scope["url_route"]["kwargs"]["cours"]
        self.users_list.append(self.channel_name)
        await self.channel_layer.group_add(self.cours, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):

        index = next(
            (
                index
                for index, d in enumerate(self.users_list)
                if d.get("channel") == self.channel_name
            ),
            None,
        )
        self.users_list.pop(index)
        print(
            self.channel_name
            + " just disconnected, here is the list after removing whatever he had "
        )
        print(self.users_list)

        await self.channel_layer.group_discard(self.cours, self.channel_name)
        await self.channel_layer.group_send(
            self.cours, {"type": "send.sdp", "message": "Someone disconnected"}
        )

    async def receive(self, text_data):
        received_data = json.loads(text_data)
        action = received_data["action"]
        # print("received a " + action)

        if action == "get-all":
            self.users_list.remove(self.channel_name)
            print("before appending myself  : ")
            print(self.users_list)
            returned_users_list = filter(
                lambda user: user["channel"] != self.channel_name, self.users_list
            )
            self.users_list.append(
                {"channel": self.channel_name, "userdata": received_data["userdata"]}
            )

            print("after appending myself  : ")
            print(self.users_list)

            await self.channel_layer.send(
                self.channel_name,
                {
                    "type": "send.sdp",
                    "message": {
                        "users": list(returned_users_list),
                        "action": action,
                        "answer_at": self.channel_name,
                    },
                },
            )
            return
        if action == "user-joined":
            await self.channel_layer.send(
                received_data["peerChannel"],
                {
                    "type": "send.sdp",
                    "message": {
                        "action": action,
                        "userdata": received_data["userdata"],
                        "signal": received_data["signal"],
                        "sent_from": received_data["peerChannel"],
                        "answer_at": self.channel_name,
                    },
                },
            )
            return
        if action == "received-answer":
            await self.channel_layer.send(
                received_data["sendTo"],
                {
                    "type": "send.sdp",
                    "message": {
                        "action": action,
                        "signal": received_data["signal"],
                        "sent_from": received_data["sentFrom"],
                    },
                },
            )
            return
        # if action == "new-offer" or action == "new-answer":
        #     destination_channel = received_data["message"]["expects_answer_at"]
        #     received_data["message"]["expects_answer_at"] = self.channel_name
        #     # received_data["channel_name"] = self.channel_name
        #     await self.channel_layer.send(
        #         destination_channel, {"type": "send.sdp", "message": received_data}
        #     )
        #     return
        # received_data["message"]["expects_answer_at"] = self.channel_name
        # await self.channel_layer.group_send(
        #     self.cours, {"type": "send.sdp", "message": received_data}
        # )

    async def send_sdp(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps(message))
