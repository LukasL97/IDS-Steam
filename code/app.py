
import random as rn

import wx
from wx.adv import BitmapComboBox


class AppFrame(wx.Frame):

    def __init__(self, tags, genres):
        super().__init__(parent=None, title='Create a successful video game!', size=(1000, 800))

        self.tags = tags
        self.tag_active = {tag: False for tag in self.tags}
        self.genres = genres
        self.active_genre = self.genres[0]
        self.active_price = 0
        self.price_step = 5

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

        self.normal_font = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.LIGHT)
        self.bold_font = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)

        tag_btn_grid_sizer = wx.GridSizer(10, 0, 0)
        sizer.Add(tag_btn_grid_sizer)

        self.tag_btns = {}
        for tag in self.tags:
            tag_btn = wx.Button(panel, label=tag)
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

        self.update_view_with_new_popularity_estimates()
        self.Show()

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

    def update_view_with_new_popularity_estimates(self):
        print('TODO: calculate them actually')

        for i, genre in enumerate(self.genres):
            color = rn.choice(['red', 'green'])
            intensity = rn.randint(0, 156)
            if color == 'green':
                self.genre_menu.SetItemBitmap(i, bitmap=wx.Bitmap.FromRGBA(16, 16, red=255 - intensity, green=255, blue=255 - intensity, alpha=255))
            else:
                self.genre_menu.SetItemBitmap(i, bitmap=wx.Bitmap.FromRGBA(16, 16, red=255, green=255 - intensity, blue=255 - intensity, alpha=255))

        for tag, tag_btn in self.tag_btns.items():
            color = rn.choice(['red', 'green'])
            intensity = rn.randint(0, 156)
            if color == 'green':
                tag_btn.SetBackgroundColour(wx.Colour(255 - intensity, 255, 255 - intensity))
            else:
                tag_btn.SetBackgroundColour(wx.Colour(255, 255 - intensity, 255 - intensity))

        for btn in [self.price_down_btn, self.price_up_btn]:
            color = rn.choice(['red', 'green'])
            intensity = rn.randint(0, 156)
            if color == 'green':
                btn.SetBackgroundColour(wx.Colour(255 - intensity, 255, 255 - intensity))
            else:
                btn.SetBackgroundColour(wx.Colour(255, 255 - intensity, 255 - intensity))

        estimated_players = rn.randint(0, 1000000)
        self.player_estimate_text.SetLabel('Estimated Players: %d' % estimated_players)


if __name__ == '__main__':
    app = wx.App()
    tags = ['TAG ' + str(i) for i in range(100)]
    genres = ['GENRE ' + str(i) for i in range(20)]
    frame = AppFrame(tags, genres)
    app.MainLoop()
