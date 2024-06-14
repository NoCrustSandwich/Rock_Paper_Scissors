import GAME_DATA_BANK

# Dictionary containing the effects on agility of each tile
TILE_AGILITY_EFFECTS = GAME_DATA_BANK.TILE_AGILITY_EFFECTS().DATA



# AI bot responsible for making moves of NPC pieces
class AI_bot:
    def __init__(self):
        """
        Initialize the AI bot.
        """
        pass

# Represents characters on the grid
class Character:
    def __init__(self, titles, name, character_id, LVL, current_HP, base_Max_HP, base_ATK, SHIELD, base_AGI, statuses, equipment):
        """
        Initialize a character.

        :param titles: Titles of the character.
        :param name: Name of the character.
        :param character_id: Unique identifier for the character.
        :param LVL: Level of the character.
        :param current_HP: Current HP of the character.
        :param max_HP: Maximum HP of the character.
        :param ATK: Attack value of the character.
        :param DEF: Defense value of the character.
        :param AGI: Agility value of the character.
        :param statuses: Status effects on the character.
        :param equipment: Equipment of the character.
        """
        self.titles = titles
        self.name = name
        self.id = character_id
        self.LVL = LVL
        self.current_HP = current_HP
        self.max_HP = base_Max_HP
        self.ATK = base_ATK
        self.SHIELD = SHIELD
        self.AGI = base_AGI
        self.statuses = statuses
        self.equipment = equipment
        self.is_Dead = False
        self.has_turn = True
        self.no_corpse = False
       

    def LVL_up(self):
        """
        Level up the character.
        """
        self.LVL += 1
        
    def take_damage(self, incoming_damage):
        """
        Apply damage to the character, reducing HP.

        :param incoming_damage: Amount of damage to take.
        """

        if self.SHIELD > 0:
            incoming_damage -= self.SHIELD

            if incoming_damage < 0:
                self.SHIELD = -(incoming_damage)
                return

        self.current_HP -= incoming_damage

        if self.current_HP <= 0:
            self.is_Dead = True

    def receive_healing(self, incoming_heal):
        """
        Heal the character, increasing HP.

        :param incoming_heal: Amount of healing to receive.
        """
        self.current_HP += incoming_heal

        # Prevents "overhealing"
        if self.current_HP > self.max_HP:
            self.current_HP = self.max_HP

    def increase_max_HP(self, increase_in_Max_HP):
        """
        Increase the maximum HP of the character.

        :param increase_in_Max_HP: Amount to increase max HP.
        """
        self.max_HP += increase_in_Max_HP

    def increase_ATK(self, increase_in_ATK):
        """
        Increase the attack value of the character.

        :param increase_in_ATK: Amount to increase attack.
        """
        self.ATK += increase_in_ATK

    def increase_AGI(self, increase_in_AGI):
        """
        Increase the agility value of the character.

        :param increase_in_AGI: Amount to increase agility.
        """
        self.AGI += increase_in_AGI

    def increase_SHIELD(self, increase_in_SHIELD):
        """
        Increase the defense value of the character.

        :param increase_in_DEF: Amount to increase defense.
        """
        self.SHIELD += increase_in_SHIELD

    def decrease_max_HP(self, decrease_in_Max_HP):
        """
        Decrease the maximum HP of the character.

        :param decrease_in_Max_HP: Amount to decrease max HP.
        """
        self.max_HP -= decrease_in_Max_HP

        if self.max_HP < 1:
            self.max_HP = 1

    def decrease_ATK(self, decrease_in_ATK):
        """
        Decrease the attack value of the character.

        :param decrease_in_ATK: Amount to decrease attack.
        """
        self.ATK -= decrease_in_ATK

        if self.ATK < 0:
            self.ATK = 0

    def decrease_AGI(self, decrease_in_AGI):
        """
        Decrease the agility value of the character.

        :param decrease_in_AGI: Amount to decrease agility.
        """
        self.AGI -= decrease_in_AGI

        if self.AGI < 1:
            self.AGI = 1

    def decrease_SHIELD(self, decrease_in_SHIELD):
        """
        Decrease the defense value of the character.

        :param decrease_in_DEF: Amount to decrease defense.
        """
        self.SHIELD -= decrease_in_SHIELD

        if self.SHIELD < 0:
            self.SHIELD = 0

# Represents the battle environment, and keeps track of its state
class Battle_Grid:
    def __init__(self, grid_tile_info, player_characters, opponent_characters):
        """
        Initialize the battle grid.

        :param dimensions: Dimensions of the grid.
        :param grid_tile_info: Information about each tile in the grid.
        :param player_characters: List of player characters.
        :param opponent_characters: List of opponent characters.
        """
        self.dimensions = [len(grid_tile_info),len(grid_tile_info[0])]

        # example grid_tile_info element = "g01*P01#01" 
        # G01 = Grass tile, character image id = P01 present on the tile, character id = #01
        self.grid_tile_info = grid_tile_info
        self.player_characters = player_characters
        self.opponent_characters = opponent_characters
        self.round_count = 0
        self.player_turn = True
        self.battle_end = False
        self.tile_selected = False
        self.selected_tile_position = [-1, -1]
        self.available_move_tiles = None
        self.selected_character = None

    # Sets the turn to be the player's
    def set_turn_player(self):
        """
        Set the current turn to be the player's turn.
        """
        self.player_turn = True

    # Sets the turn to be the opponent's
    def set_turn_opponent(self):
        """
        Set the current turn to be the opponent's turn.
        """
        self.player_turn = False

    # Returns list of available moves for the given character and their position based on agility value
    def get_characters_available_moves(self, character_tile_position):
        """
        Get the list of available moves for the selected character.

        :param character_tile_position: Current position of the character on the grid.
        :return: List of available move positions.
        """
        available_moves = []

        # Calculate true agility considering the tile effect
        true_agility = self.selected_character.AGI + TILE_AGILITY_EFFECTS[self.grid_tile_info[character_tile_position[0]][character_tile_position[1]][0]]

        # Makes sure true agility is always at least 1 (or else characters could get stuck on a tile if agility too low)
        if true_agility < 1:
            true_agility = 1
        
        # Initial moves based on true agility
        available_moves.append([character_tile_position[0] - 1, character_tile_position[1]])
        available_moves.append([character_tile_position[0] + 1, character_tile_position[1]])
        available_moves.append([character_tile_position[0], character_tile_position[1] + 1])
        available_moves.append([character_tile_position[0], character_tile_position[1] - 1])
        last_added_moves = available_moves.copy()

        # Determines all possible end tiles based on character agility
        for _ in range(true_agility - 1):
            for move in last_added_moves:
                temp_array = []
                temp_array.append([move[0] - 1, move[1]])
                temp_array.append([move[0] + 1, move[1]])
                temp_array.append([move[0], move[1] + 1])
                temp_array.append([move[0], move[1] - 1])

                # Combines the new moves with old moves but removes the duplicates
                available_moves = list(set(available_moves) | set(temp_array))
                last_added_moves = temp_array.copy()

        return available_moves.copy()

    # Returns the character at the tile based on the character ID
    def get_character_at_tile(self, tile_position):
        
        tile_info = self.grid_tile_info[tile_position[0]][tile_position[1]]
        

        if tile_info[4] == "P":
            return self.player_characters[tile_info[7:10]]
        
        elif tile_info[4] == "E":
            return self.opponent_characters[tile_info[7:10]]
        else:
            return None


    # Attempts to select tile
    def select_tile_attempt(self, tile_position):
        """
        Attempt to select a tile and set the selected character if valid.

        :param tile_position: Position of the tile to select.
        """
        
        character_at_tile = self.get_character_at_tile(tile_position)
        try:
            if self.grid_tile_info[tile_position[0]][tile_position[1]][4] == "P" and character_at_tile.has_turn:
               
                self.selected_tile_position = tile_position
                self.tile_selected = True

                self.selected_character = character_at_tile

                if self.selected_character == None:
                    print("ERROR: Character id at tile, not found in player_character list")
                    return

                self.available_move_tiles = self.get_characters_available_moves(self.selected_tile_position)
        
        except AttributeError:
            print(f"ERROR: No Character Present at the tile position [Row: {tile_position[0]}, Column: {tile_position[1]}]")
            print(f"Info present at selected tile: {self.grid_tile_info[tile_position[0]][tile_position[1]]}")
            pass
        
        print(self.selected_tile_position)
        return

    # Updates character position
    def update_character_position(self, new_tile_position):
        """
        Update the character's position on the grid.

        :param new_tile_position: New position to move the character to.
        """
        # Get the character info from the current tile
        character_info = self.grid_tile_info[self.selected_tile_position[0]][self.selected_tile_position[1]][4:10]
        
        # Move the character to the new tile
        current_tile_value = self.grid_tile_info[new_tile_position[0]][new_tile_position[1]]
        new_tile_value = current_tile_value[:4] + character_info
        self.grid_tile_info[new_tile_position[0]][new_tile_position[1]] = new_tile_value
        


        # Remove the character from the previous tile
        old_tile_value = self.grid_tile_info[self.selected_tile_position[0]][self.selected_tile_position[1]]
        cleaned_old_tile_value = old_tile_value[:4] + "___#__"
        self.grid_tile_info[self.selected_tile_position[0]][self.selected_tile_position[1]] = cleaned_old_tile_value

        return

    # Attempts to make move from prior selected tile to newly selected tile, if selected tile is invalid unselect first tile
    def selected_tile_move_attempt(self, new_tile_position):
        """
        Attempt to move the selected character to a new tile.

        :param new_tile_position: Position of the new tile to move to.
        """
        if new_tile_position in self.available_move_tiles:
            if self.grid_tile_info[new_tile_position[0]][new_tile_position[1]][4:7] == "___":

                self.update_character_position(new_tile_position)
                self.selected_character.has_turn = False
                self.tile_selected = False
                return
            elif self.grid_tile_info[new_tile_position[0]][new_tile_position[1]][4] == "E":
                enemy_character  = self.opponent_characters[self.grid_tile_info[new_tile_position[0]][new_tile_position[1]][7:10]]
                enemy_character.take_damage(self.selected_character.ATK)

                if enemy_character.is_Dead:
                    self.grid_tile_info[new_tile_position[0]][new_tile_position[1]][4] = "C"

                self.selected_character.has_turn = False
                self.tile_selected = False
                return
            elif self.grid_tile_info[new_tile_position[0]][new_tile_position[1]][4] == "C":
                enemy_character = self.opponent_characters[int(self.grid_tile_info[new_tile_position[0]][new_tile_position[1]][5:7]) - 1]
                enemy_character.take_damage(self.selected_character.ATK)

                if enemy_character.is_Dead:
                    self.grid_tile_info[new_tile_position[0]][new_tile_position[1]][4] = "C"

                self.selected_character.has_turn = False
                self.tile_selected = False
                return

            else:
                print("ERROR: invalid destination")
                self.tile_selected = False
                self.selected_tile_position = [-1, -1]
                self.available_move_tiles = None
                self.selected_character = None
                return
        else:

            print("ERROR: new_tile_position not in self.available_move_tiles")
            self.tile_selected = False
            self.selected_tile_position = [-1, -1]
            self.available_move_tiles = None
            self.selected_character = None
            return
