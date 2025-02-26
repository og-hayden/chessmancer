from typing import Tuple, List, Dict, Any, Optional
import pygame
import math

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
        # Convert position to float for smooth movement
        self.position = (float(position[0]), float(position[1]))
        self.inventory = inventory
        self.health = 100
        self.max_health = 100
        self.movement_range = 4  # Used for combat, not for exploration
        self.vision_range = 5  # How far the player can see
        
        # Player stats
        self.command = inventory.command_stat
        self.tactics = inventory.tactics_stat
        self.perception = inventory.perception_stat
        self.arcana = inventory.arcana_stat
        
        # Fluid movement properties
        self.velocity = [0.0, 0.0]  # [x, y] velocity
        self.max_speed = 0.15  # Maximum movement speed
        self.acceleration = 0.02  # How quickly player accelerates
        self.deceleration = 0.1  # How quickly player decelerates when no input
        self.is_moving = False
        
        # Movement keys state
        self.movement_keys = {
            pygame.K_w: False,
            pygame.K_UP: False,
            pygame.K_s: False,
            pygame.K_DOWN: False,
            pygame.K_a: False,
            pygame.K_LEFT: False,
            pygame.K_d: False,
            pygame.K_RIGHT: False
        }
        
        # Interaction state
        self.interacting_with = None
    
    def set_movement_key(self, key: int, pressed: bool) -> None:
        """
        Set the state of a movement key.
        
        Args:
            key: The key code
            pressed: Whether the key is pressed
        """
        if key in self.movement_keys:
            self.movement_keys[key] = pressed
    
    def update_velocity(self) -> None:
        """Update the player's velocity based on input keys."""
        # Calculate target velocity based on input
        target_x, target_y = 0.0, 0.0
        
        # Vertical movement
        if self.movement_keys[pygame.K_w] or self.movement_keys[pygame.K_UP]:
            target_y = -self.max_speed
        elif self.movement_keys[pygame.K_s] or self.movement_keys[pygame.K_DOWN]:
            target_y = self.max_speed
        
        # Horizontal movement
        if self.movement_keys[pygame.K_a] or self.movement_keys[pygame.K_LEFT]:
            target_x = -self.max_speed
        elif self.movement_keys[pygame.K_d] or self.movement_keys[pygame.K_RIGHT]:
            target_x = self.max_speed
        
        # Normalize diagonal movement
        if target_x != 0 and target_y != 0:
            magnitude = math.sqrt(target_x**2 + target_y**2)
            target_x = target_x / magnitude * self.max_speed
            target_y = target_y / magnitude * self.max_speed
        
        # Smoothly adjust current velocity toward target
        if target_x != 0:
            self.velocity[0] += (target_x - self.velocity[0]) * self.acceleration
        else:
            # Decelerate when no input
            self.velocity[0] *= (1 - self.deceleration)
            if abs(self.velocity[0]) < 0.01:
                self.velocity[0] = 0
        
        if target_y != 0:
            self.velocity[1] += (target_y - self.velocity[1]) * self.acceleration
        else:
            # Decelerate when no input
            self.velocity[1] *= (1 - self.deceleration)
            if abs(self.velocity[1]) < 0.01:
                self.velocity[1] = 0
        
        # Update moving state
        self.is_moving = self.velocity[0] != 0 or self.velocity[1] != 0
    
    def update_position(self, dungeon) -> bool:
        """
        Update the player's position based on velocity and check for collisions.
        
        Args:
            dungeon: The dungeon the player is in
            
        Returns:
            True if the position was updated, False otherwise
        """
        if not self.is_moving:
            return False
        
        # Calculate new position
        new_x = self.position[0] + self.velocity[0]
        new_y = self.position[1] + self.velocity[1]
        
        # Check for collisions and adjust position
        # First try moving in both directions
        if dungeon.is_walkable(int(new_x), int(new_y)):
            self.position = (new_x, new_y)
            return True
        
        # If that fails, try moving only horizontally
        if dungeon.is_walkable(int(new_x), int(self.position[1])):
            self.position = (new_x, self.position[1])
            self.velocity[1] = 0  # Stop vertical movement
            return True
        
        # If that fails, try moving only vertically
        if dungeon.is_walkable(int(self.position[0]), int(new_y)):
            self.position = (self.position[0], new_y)
            self.velocity[0] = 0  # Stop horizontal movement
            return True
        
        # If all movement is blocked, stop
        self.velocity = [0.0, 0.0]
        return False
    
    def get_current_position(self) -> Tuple[float, float]:
        """
        Get the current position of the player.
        
        Returns:
            The current (x, y) position
        """
        return self.position
    
    def get_tile_position(self) -> Tuple[int, int]:
        """
        Get the current tile position of the player (rounded to integers).
        
        Returns:
            The current tile (x, y) position
        """
        return (int(round(self.position[0])), int(round(self.position[1])))
    
    def interact(self, dungeon) -> Optional[Any]:
        """
        Interact with an entity in an adjacent tile.
        
        Args:
            dungeon: The dungeon the player is in
            
        Returns:
            The result of the interaction, if any
        """
        # Check adjacent tiles for interactive entities
        x, y = self.get_tile_position()
        
        for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
            check_x, check_y = x + dx, y + dy
            
            if 0 <= check_x < dungeon.width and 0 <= check_y < dungeon.height:
                entity = dungeon.get_entity_at(check_x, check_y)
                
                if entity and hasattr(entity, 'interact'):
                    self.interacting_with = entity
                    return entity
                elif entity:
                    # If the entity doesn't have an interact method, just return it
                    # This allows the main game to handle different entity types
                    self.interacting_with = entity
                    return entity
        
        return None
    
    def end_interaction(self) -> None:
        """End the current interaction."""
        self.interacting_with = None
    
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