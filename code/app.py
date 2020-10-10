
import random as rn

import joblib
import numpy as np
import wx
from wx.adv import BitmapComboBox


class AppFrame(wx.Frame):

    def __init__(self, tags, genres, fir):
        super().__init__(parent=None, title='Create a successful video game!', size=(1600, 800))

        self.model = self.get_model()

        self.fir = fir

        self.tags = tags
        self.tag_active = {tag: False for tag in self.tags}
        self.genres = genres
        self.active_genre = self.genres[0]
        self.active_price = 0
        self.price_step = 5
        self.active_years_since_release = 0
        self.years_since_release_step = 1

        panel = wx.Panel(self)
        panel.SetBackgroundColour('white')

        sizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(sizer)

        self.player_estimate_text = wx.StaticText(panel, label='Estimated Players: 0')
        self.player_estimate_text.SetFont(wx.Font(30, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        sizer.Add(self.player_estimate_text, 0, wx.ALL | wx.EXPAND, 5)

        self.genre_text = wx.StaticText(panel, label='Select a category:')
        self.genre_text.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        sizer.Add(self.genre_text, 0, wx.ALL | wx.EXPAND, 5)

        self.genre_menu = wx.adv.BitmapComboBox(panel)
        for genre in self.genres:
            self.genre_menu.Append(genre, bitmap=wx.Bitmap.FromRGBA(16, 16, red=255, green=255, blue=255, alpha=255))
        self.genre_menu.SetSelection(0)
        self.genre_menu.Bind(wx.EVT_COMBOBOX, self.select_genre)
        sizer.Add(self.genre_menu, 0, wx.ALL | wx.EXPAND, 5)

        self.tags_text = wx.StaticText(panel, label='Select some tags:')
        self.tags_text.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        sizer.Add(self.tags_text, 0, wx.ALL | wx.EXPAND, 5)

        self.normal_font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.LIGHT)
        self.bold_font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD)

        tag_btn_grid_sizer = wx.GridSizer(10, 0, 0)
        sizer.Add(tag_btn_grid_sizer)

        self.tag_btns = {}
        for tag in self.tags:
            tag_btn = wx.Button(panel, label=tag, size=(150, 30))
            tag_btn.SetFont(self.normal_font)
            tag_btn.Bind(wx.EVT_BUTTON, self.toggle_tag_btn(tag_btn))
            tag_btn_grid_sizer.Add(tag_btn, 0, wx.ALL | wx.CENTER, 5)
            self.tag_btns[tag] = tag_btn

        self.price_text = wx.StaticText(panel, label='Select a price:')
        self.price_text.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        sizer.Add(self.price_text, 0, wx.ALL | wx.EXPAND, 5)

        price_grid_sizer = wx.GridSizer(3, 0, 0)
        sizer.Add(price_grid_sizer)
        self.price_down_btn = wx.Button(panel, label='-%d€' % self.price_step)
        self.price_down_btn.SetFont(self.bold_font)
        self.price_down_btn.Bind(wx.EVT_BUTTON, self.decrease_price)
        price_grid_sizer.Add(self.price_down_btn, 0, wx.ALL | wx.EXPAND, 5)
        self.active_price_text = wx.StaticText(panel, label=('%d€' % self.active_price).rjust(4))
        self.active_price_text.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        price_grid_sizer.Add(self.active_price_text, 0, wx.ALL | wx.EXPAND, 5)
        self.price_up_btn = wx.Button(panel, label='+%d€' % self.price_step)
        self.price_up_btn.SetFont(self.bold_font)
        self.price_up_btn.Bind(wx.EVT_BUTTON, self.increase_price)
        price_grid_sizer.Add(self.price_up_btn, 0, wx.ALL | wx.EXPAND, 5)

        self.years_since_release_text = wx.StaticText(panel, label='Estimate players for ... years since release:')
        self.years_since_release_text.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        sizer.Add(self.years_since_release_text, 0, wx.ALL | wx.EXPAND, 5)

        years_grid_sizer = wx.GridSizer(3, 0, 0)
        sizer.Add(years_grid_sizer)
        self.years_down_btn = wx.Button(panel, label='-%d' % self.years_since_release_step)
        self.years_down_btn.SetFont(self.bold_font)
        self.years_down_btn.Bind(wx.EVT_BUTTON, self.decrease_years_since_release)
        years_grid_sizer.Add(self.years_down_btn, 0, wx.ALL | wx.EXPAND, 5)
        self.active_years_since_release_text = wx.StaticText(panel, label=('%d' % self.active_years_since_release).rjust(4))
        self.active_years_since_release_text.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        years_grid_sizer.Add(self.active_years_since_release_text, 0, wx.ALL | wx.EXPAND, 5)
        self.years_up_btn = wx.Button(panel, label='+%d' % self.years_since_release_step)
        self.years_up_btn.SetFont(self.bold_font)
        self.years_up_btn.Bind(wx.EVT_BUTTON, self.increase_years_since_release)
        years_grid_sizer.Add(self.years_up_btn, 0, wx.ALL | wx.EXPAND, 5)

        self.update_view_with_new_popularity_estimates()
        self.Show()

    def get_model(self):
        return joblib.load('../trained_model.pkl')

    def select_genre(self, s):
        self.active_genre = self.genres[self.genre_menu.GetSelection()]
        self.update_view_with_new_popularity_estimates()

    def toggle_tag_btn(self, tag_btn):
        def on_toggle(s):
            tag = tag_btn.GetLabel()
            if self.tag_active[tag]:
                self.tag_active[tag] = False
                tag_btn.SetFont(self.normal_font)
            else:
                self.tag_active[tag] = True
                tag_btn.SetFont(self.bold_font)
            self.update_view_with_new_popularity_estimates()
        return on_toggle

    def decrease_price(self, s):
        self.active_price -= self.price_step
        self.active_price_text.SetLabel(('%d€' % self.active_price).rjust(4))
        self.update_view_with_new_popularity_estimates()

    def increase_price(self, s):
        self.active_price += self.price_step
        self.active_price_text.SetLabel(('%d€' % self.active_price).rjust(4))
        self.update_view_with_new_popularity_estimates()

    def decrease_years_since_release(self, s):
        self.active_years_since_release -= self.years_since_release_step
        self.active_years_since_release_text.SetLabel(('%d' % self.active_years_since_release).rjust(4))
        self.update_view_with_new_popularity_estimates()

    def increase_years_since_release(self, s):
        self.active_years_since_release += self.years_since_release_step
        self.active_years_since_release_text.SetLabel(('%d' % self.active_years_since_release).rjust(4))
        self.update_view_with_new_popularity_estimates()

    def get_state_as_input(self, genre, tags, price, years_since_release):
        input = np.zeros(self.fir.num_features())
        input[fir.get_genre_index(genre)] = 1.0
        for tag in tags:
            input[fir.get_tag_index(tag)] = 1.0
        input[fir.get_price_index()] = price
        input[fir.get_years_since_release_index()] = years_since_release
        return input

    def get_current_state_as_input(self):
        return self.get_state_as_input(
            self.active_genre,
            [tag for tag, active in self.tag_active.items() if active],
            self.active_price,
            self.active_years_since_release
        ).reshape((1, self.fir.num_features()))

    def get_genre_variations_as_inputs(self):
        inputs = np.zeros((len(self.genres), self.fir.num_features()))
        for idx, genre in enumerate(self.genres):
            inputs[idx] = self.get_state_as_input(
                genre,
                [tag for tag, active in self.tag_active.items() if active],
                self.active_price,
                self.active_years_since_release
            )
        return inputs

    def get_tag_variations_as_inputs(self):
        inputs = np.zeros((len(self.tag_active), self.fir.num_features()))
        for idx, (tag, active) in enumerate(self.tag_active.items()):
            varied_tag_active = self.tag_active.copy()
            varied_tag_active[tag] = not active
            inputs[idx] = self.get_state_as_input(
                self.active_genre,
                [tag for tag, active in varied_tag_active.items() if active],
                self.active_price,
                self.active_years_since_release
            )
        return inputs

    def get_price_variations_as_inputs(self):
        inputs = np.zeros((2, self.fir.num_features()))
        for idx, price_diff in enumerate([-self.price_step, self.price_step]):
            inputs[idx] = self.get_state_as_input(
                self.active_genre,
                [tag for tag, active in self.tag_active.items() if active],
                self.active_price + price_diff,
                self.active_years_since_release
            )
        return inputs

    def get_years_since_release_variations_as_inputs(self):
        inputs = np.zeros((2, self.fir.num_features()))
        for idx, years_diff in enumerate([-self.years_since_release_step, self.years_since_release_step]):
            inputs[idx] = self.get_state_as_input(
                self.active_genre,
                [tag for tag, active in self.tag_active.items() if active],
                self.active_price,
                self.active_years_since_release + years_diff
            )
        return inputs

    def predict_batch(self, input):
        return self.model.predict(input)

    def transform_label_to_original(self, labels):
        return np.exp(labels)

    def get_max_pred_diff_from_current(self, preds, current_pred):
        return np.max(np.abs(preds - current_pred))

    def get_rgb_for_prediction(self, pred, current_pred, max_pred_diff_from_current):
        max_intensity = 155
        intensity = int(max_intensity * abs(pred - current_pred) / max_pred_diff_from_current)
        if pred >= current_pred:
            return (255 - intensity, 255, 255 - intensity)
        else:
            return (255, 255 - intensity, 255 - intensity)

    def update_view_with_new_popularity_estimates(self):
        inputs = np.concatenate([
            self.get_current_state_as_input(),
            self.get_genre_variations_as_inputs(),
            self.get_tag_variations_as_inputs(),
            self.get_price_variations_as_inputs(),
            self.get_years_since_release_variations_as_inputs()
        ])

        estimates = self.predict_batch(inputs)
        current_estimate = estimates[0]
        max_estimate_diff = self.get_max_pred_diff_from_current(estimates, current_estimate)
        estimates_rgb = [self.get_rgb_for_prediction(estimate, current_estimate, max_estimate_diff) for estimate in estimates]
        genre_estimates_rgb = estimates_rgb[1:1+len(self.genres)]
        tag_estimates_rgb = estimates_rgb[1+len(self.genres):1+len(self.genres)+len(self.tags)]
        price_estimates_rgb = estimates_rgb[-4:-2]
        years_since_release_estimates_rgb = estimates_rgb[-2:]

        estimated_players = self.transform_label_to_original(current_estimate)
        self.player_estimate_text.SetLabel('Estimated Players: %d' % estimated_players)

        for i, (genre, (r, g, b)) in enumerate(zip(self.genres, genre_estimates_rgb)):
            self.genre_menu.SetItemBitmap(i, bitmap=wx.Bitmap.FromRGBA(16, 16, red=r, green=g, blue=b, alpha=255))

        for (tag, tag_btn), (r, g, b) in zip(self.tag_btns.items(), tag_estimates_rgb):
            tag_btn.SetBackgroundColour(wx.Colour(r, g, b))

        for price_btn, (r, g, b) in zip([self.price_down_btn, self.price_up_btn], price_estimates_rgb):
            price_btn.SetBackgroundColour(wx.Colour(r, g, b))

        for years_btn, (r, g, b) in zip([self.years_down_btn, self.years_up_btn], years_since_release_estimates_rgb):
            years_btn.SetBackgroundColour(wx.Colour(r, g, b))


def get_tags(limit=100):
    with open('../tags_ordered.txt', mode='r', encoding='utf8') as tags_file:
        tags = tags_file.read().split('\n')
    tags = [t[4:] for t in tags]
    return tags[:limit]

def get_genres():
    return [
        'Action Games',
        'Indie Games',
        'Casual Games',
        'Adventure Games',
        'RPG Games',
        'Simulation Games',
        'Strategy Games',
        'Free to Play Games',
        'Racing Games',
        'Sports Games',
        'Early Access Games',
        'Massively Multiplayer Games',
        'Violent Games',
        'Sexual Content Games',
        'Gore Games',
        'Nudity Games',
        'Simulation'
    ]

class FeatureIndexResolver(object):

    def __init__(self):
        with open('../ausgabe_namen_x.csv', mode='r', encoding='utf8') as features_file:
            features = features_file.read().split(',')
        features = [f.strip()[1:-1] for f in features]
        print(features)
        self.features = {f: i for i, f in enumerate(features)}

    def num_features(self):
        return len(self.features)

    def get_tag_index(self, tag):
        return self.features['tag_' + tag]

    def get_genre_index(self, genre):
        return self.features['category_' + genre]

    def get_price_index(self):
        return self.features['price']

    def get_years_since_release_index(self):
        return self.features['years_since_release']


if __name__ == '__main__':
    app = wx.App()
    tags = get_tags(100)
    genres = get_genres()
    fir = FeatureIndexResolver()
    frame = AppFrame(tags, genres, fir)
    app.MainLoop()
