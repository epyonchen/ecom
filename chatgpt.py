#!/usr/bin/python
# coding=utf-8
import openai


class Conversation:
    # initial
    def __init__(self, prompt, round):
        self.prompt = prompt
        self.round = round
        self.messages = []
        self.messages.append({"role": "system", "content": self.prompt})

    # ask a new question    
    def ask(self, question):
        try:
            question_input = {"role": "user", "content": question}
            self.messages.append(question_input)
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self.messages,
                temperature=1,
                max_tokens=2048,
                top_p=1,
            )
        except Exception as e:
            print(e)
            return e

        message = response["choices"][0]["message"]["content"]

        self.messages.append({"role": "assistant", "content": message})

        # summarize question if exceeding lenth
        if len(self.messages) > self.round * 2 + 1:
            text = self._build_message()
            # print (text)
            # print ("=====summarize=====")
            summarize = self.summarize(text)
            # print (summarize)
            # print ("=====summarize=====")
            self.messages = []
            self.messages.append({"role": "system", "content": summarize})
        return message

    def summarize(self, text, max_tokens=200):
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=text + "\n\n请总结一下上面User和Assistant聊了些什么：\n",
            max_tokens=max_tokens,
        )
        return response["choices"][0]["text"]

    def _build_message(self):
        text = ""
        for message in self.messages:
            if message["role"] == "user":
                text += "User : " + message["content"] + "\n\n"
            if message["role"] == "assistant":
                text += "Assistant : " + message["content"] + "\n\n"
        return text
