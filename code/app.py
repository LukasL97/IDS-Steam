
import wx
import random as rn

class AppFrame(wx.Frame):

    def __init__(self, tags):
        super().__init__(parent=None, title='Create a successful video game!', size=(1000, 800))

        self.tags = tags
        self.tag_active = {tag: False for tag in self.tags}

        panel = wx.Panel(self)
        panel.SetBackgroundColour('white')

        sizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(sizer)

        self.player_estimate_text = wx.StaticText(panel, label='Estimated Players: 0')
        self.player_estimate_text.SetFont(wx.Font(30, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        sizer.Add(self.player_estimate_text, 0, wx.ALL | wx.EXPAND, 5)

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

        self.update_view_with_new_popularity_estimates()
        self.Show()

    def toggle_tag_btn(self, tag_btn):
        def on_toggle(s):
            tag = tag_btn.GetLabel()
            if self.tag_active[tag]:
                self.tag_active[tag] = False
                tag_btn.SetFont(self.normal_font)
            else:
                self.tag_active[tag] = True
                tag_btn.SetFont(self.bold_font)#
            self.update_view_with_new_popularity_estimates()
        return on_toggle

    def update_view_with_new_popularity_estimates(self):
        print('TODO: calculate them actually')

        for tag, tag_btn in self.tag_btns.items():
            color = rn.choice(['red', 'green'])
            intensity = rn.randint(0, 156)
            if color == 'green':
                tag_btn.SetBackgroundColour(wx.Colour(255 - intensity, 255, 255 - intensity))
            else:
                tag_btn.SetBackgroundColour(wx.Colour(255, 255 - intensity, 255 - intensity))

        estimated_players = rn.randint(0, 1000000)
        self.player_estimate_text.SetLabel('Estimated Players: %d' % estimated_players)


if __name__ == '__main__':
    app = wx.App()
    tag = ['TAG ' + str(i) for i in range(100)]
    frame = AppFrame(tag)
    app.MainLoop()
