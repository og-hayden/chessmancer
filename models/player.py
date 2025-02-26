from typing import Tuple, List, Dict, Any, Optional
import pygame

from models.player_inventory import PlayerInventory


class Player:
    """Represents the player character in the dungeon."""
    
    def __init__(self, position: Tuple[int, int], inventory: PlayerInventory):
        """
        Initialize the player.
        
        Args:
            position: (x, y) position in the dungeon
            inventory: The player's inventory
        """
        self.position = position
        self.inventory = inventory
        self.health = 100
        self.max_health = 100
        self.movement_range = 4  # Squares per turn
        self.moves_remaining = self.movement_range
        self.vision_range = 5  # How far the player can see
        
        # Player stats
        self.command = inventory.command_stat
        self.tactics = inventory.tactics_stat
        self.perception = inventory.perception_stat
        self.arcana = inventory.arcana_stat
        
        # Movement animation
        self.is_moving = False
        self.move_target = None
        self.move_progress = 0.0
        self.move_speed = 0.2  # Lower is faster
        
        # Interaction state
        self.interacting_with = None
    
    def move(self, dx: int, dy: int, dungeon) -> bool:
        """
        Move the player by the given delta if possible.
        
        Args:
            dx: Change in x position
            dy: Change in y position
            dungeon: The dungeon the player is in
            
        Returns:
            True if the move was successful, False otherwise
        """
        if self.moves_remaining <= 0 or self.is_moving:
            return False
        
        new_x = self.position[0] + dx
        new_y = self.position[1] + dy
        
        # Check if the new position is walkable
        if dungeon.is_walkable(new_x, new_y):
            # Start movement animation
            self.is_moving = True
            self.move_target = (new_x, new_y)
            self.move_progress = 0.0
            return True
        
        return False
    
    def update_movement(self) -> bool:
        """
        Update the player's movement animation.
        
        Returns:
            True if the movement is complete, False otherwise
        """
        if not self.is_moving or not self.move_target:
            return True
        
        # Update movement progress
        self.move_progress += self.move_speed
        
        if self.move_progress >= 1.0:
            # Movement complete
            self.position = self.move_target
            self.move_target = None
            self.is_moving = False
            self.moves_remaining -= 1
            return True
        
        return False
    
    def get_current_position(self) -> Tuple[float, float]:
        """
        Get the player's current position, including animation interpolation.
        
        Returns:
            (x, y) position as floats for smooth animation
        """
        if not self.is_moving or not self.move_target:
            return float(self.position[0]), float(self.position[1])
        
        # Interpolate between current position and target
        start_x, start_y = self.position
        target_x, target_y = self.move_target
        
        current_x = start_x + (target_x - start_x) * self.move_progress
        current_y = start_y + (target_y - start_y) * self.move_progress
        
        return current_x, current_y
    
    def interact(self, dungeon) -> Optional[Any]:
        """
        Interact with an entity at the player's position or adjacent to it.
        
        Args:
            dungeon: The dungeon the player is in
            
        Returns:
            The entity being interacted with, or None if no interaction occurred
        """
        # Check the player's current position
        entity = dungeon.get_entity_at(*self.position)
        if entity:
            self.interacting_with = entity
            return entity
        
        # Check adjacent tiles
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            x, y = self.position[0] + dx, self.position[1] + dy
            entity = dungeon.get_entity_at(x, y)
            
            if entity:
                self.interacting_with = entity
                return entity
        
        self.interacting_with = None
        return None
    
    def end_turn(self) -> None:
        """End the player's turn, resetting movement points."""
        self.moves_remaining = self.movement_range
    
    def take_damage(self, amount: int) -> bool:
        """
        Reduce the player's health by the given amount.
        
        Args:
            amount: Amount of damage to take
            
        Returns:
            True if the player is still alive, False otherwise
        """
        self.health = max(0, self.health - amount)
        return self.health > 0
    
    def heal(self, amount: int) -> None:
        """Heal the player by the given amount."""
        self.health = min(self.max_health, self.health + amount)
    
    def update_stats_from_inventory(self) -> None:
        """Update the player's stats from their inventory."""
        self.command = self.inventory.command_stat
        self.tactics = self.inventory.tactics_stat
        self.perception = self.inventory.perception_stat
        self.arcana = self.inventory.arcana_stat
        
        # Update derived stats
        self.vision_range = 5 + (self.perception // 3)  # +1 vision per 3 perception 