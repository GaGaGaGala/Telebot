import random

class RandomCompliments:
    compliments = [
        ["Ты, как ветер, свободная, непредсказуемая и красивая. "],
        ["Клевая футболка."],
        ["Я люблю наблюдать, как ты свободно движешься по жизни и не боишься быть самой собой."],
        [" И кстати, у вас милый ремонт!"],
        ["Ты вдохновляешь меня быть лучшим человеком и жить полной жизнью."],
        ["Ты всегда выглядишь потрясающе, даже если ничего особенного для этого не делаешь."],
        ["Как вам удаётся так хорошо выглядеть?"],
        ["У тебя всегда стильные и яркие образы!"]
    ]

    def _init_(self):
        self.compliments = []

    def get_compliment(self):
        return random.choice(self.compliments)


compl = RandomCompliments()


def flip_a_coin():
    return random.choice(['Heads', 'Tails'])