class MenuController:
    def __init__(self, oled, x, y, w, h, char_height=10):
        self.oled = oled
        self.cursor = 0
        self.current_offset = 0
        self.current_items = []
        self.menu_x = x
        self.menu_y = y
        self.menu_w = w
        self.menu_h = h
        self.char_height = char_height

    def rect_row(self, row_num, padding=0, clear=False):
        color = 1 if not clear else 0
        self.oled.rect(self.menu_x, self.menu_y + (row_num * self.char_height), self.menu_w, self.char_height, color)

    def clear_menu(self):
        self.oled.fill_rect(self.menu_x, self.menu_y, self.menu_w, self.menu_h, 0)

    def show_menu(self, menu_items, offset=0, cursor=0):
        self.clear_menu()
        self.current_offset = offset
        self.current_items = menu_items
        menu_items = menu_items or []
        for i in range(len(menu_items)):
            if (i+1)*self.char_height > self.menu_h:
                break
            self.oled.text(menu_items[i + offset][0], self.menu_x + 1, self.menu_y + i*self.char_height + 1, 1)
        self.show_cursor(cursor)
        
    def show_cursor(self, cursor):
        self.rect_row(cursor, clear=True)
        self.cursor = cursor
        self.rect_row(cursor, clear=False)

    def goto_cursor(self, cursor):
        if not self.current_items:
            return
        if cursor < 0: cursor = 0
        if cursor >= len(self.current_items): cursor = len(self.current_items) - 1
        items_per_page = self.menu_h // self.char_height
        if (self.current_offset <= cursor < self.current_offset + items_per_page):
            new_offset = self.current_offset
            new_cursor = cursor - self.current_offset
        else:
            new_cursor = min(items_per_page // 2, items_per_page - 1)
            new_offset = cursor - new_cursor
            if new_offset < 0:
                new_offset = 0
            if new_offset + items_per_page > len(self.current_items):
                new_offset = max(0, len(self.current_items) - items_per_page)
                new_cursor = cursor - new_offset
        self.show_menu(self.current_items, new_offset, new_cursor)

    def ensure_cursor(self):
        selected_item = self.current_items[self.current_offset + self.cursor]
        action = selected_item[1]
        exec(action, globals(), locals())
        return selected_item

