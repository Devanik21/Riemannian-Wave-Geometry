"""
agents.py — BioHyperAgent v3.0
================================
A truly bio-inspired living organism with METACOGNITIVE self-modification
and FULL SOCIAL-ECONOMIC dynamics ported from GeNeSIS.

SOUL    : Immutable spectral frequency signature  (eigenfrequency identity)
BRAIN   : HarmonicResonanceConsciousness v3.0     (wave-based cognition + meta-layer)
META    : MetaConsciousness                        (self-modifying learning rules)
BODY    : Physical presence, energy metabolism, health, aging
WILL    : Autonomous action selection — no external task, no reward shaping
DEATH   : Finite lifespan; leaves legacy artifact + apoptotic death packet

NEW in v3.0 (ported from GeNeSIS / Thermodynamic-Mind):
  Social Bonds & Trust Memory   : Persistent relationships with metabolic osmosis
  Inventory Economy              : Red/Green/Blue tokens with synergy bonus
  Role / Caste System            : Forager, Processor, Warrior, Queen
  Trade & Punish Actions         : Economic and punitive social actions
  Epigenetic ψ Inheritance       : Children inherit blended parent ψ
  Kuramoto Phase Sync            : Per-agent oscillatory phase
  Viral Gene Transfer            : H-eigenvalue meme packets
  GoL Scratchpad                 : Conway's Game of Life as internal computation
  Apoptotic Death Packets        : Broadcast H spectral fingerprint on death
  Landauer Cognitive Cost        : Thermodynamic cost of thinking
  Causal Bayesian Model          : P(R|do(A)) intervention tracking
  Weather Voting                 : Collective environmental modulation
  IQ Complexity Bonus            : ψ diversity incentive
  Circadian Internal Phase       : Circadian synchronization with seasons

Actions (20):
  Base: move (8 dirs), eat, attack, communicate, reproduce,
        invent, rest, build_artifact, absorb_artifact
  Meta: meta_invent, compose_action
  Social: trade, punish

Population: 72 initial (capped at 128 for Streamlit/K_DIM=32 performance).

Invented by Devanik & Claude (Xylia) — Event Horizon Project
"""

import numpy as np
import uuid
from typing import Optional, List, Dict, Tuple

from metacognition import (
    K_DIM, K_TASK, K_META,
    MetaConsciousness, GodelEncoder, GODEL,
    ALL_PRIMITIVES, PRIM_CATEGORY,
)
from consciousness import (
    HarmonicResonanceConsciousness, CognitionMode,
    ACTIONS, N_ACTIONS, E,
)

# ── Physics constants ────────────────────────────────────────────────────────
_BASE_FREQS = np.array([
    1.0,  2.0,  3.0,  5.0,  7.0,  11.0,  13.0,  17.0,
    19.0, 23.0, 29.0, 31.0, 37.0, 41.0,  43.0,  47.0,
    53.0, 59.0, 61.0, 67.0, 71.0, 73.0,  79.0,  83.0,
    89.0, 97.0, 101.0,103.0,107.0,109.0, 113.0, 127.0,
])  # first 32 primes


class BioHyperAgent:
    """
    One living organism inside the Hyper-Horizon simulation.

    Lifecycle:
        spawn → live (sense → decide → act → learn → evolve) → die → legacy

    Social dynamics emerge from resonance coupling, bonds, and trade.
    Technology propagates via artifact placement and absorption.
    Civilisations form when resonance-compatible agents cluster.
    Meta-learning evolves through inheritance and self-modification.
    Roles emerge from caste genes and behavioral clustering.
    """

    # ── Life constants ───────────────────────────────────────────────────────
    MAX_AGE           = -1
    BASE_METABOLISM   = 0.001
    MOVE_COST         = 0.002
    ATTACK_COST       = 0.05
    REPRODUCE_COST    = 0.35
    INVENT_COST       = 0.15
    BUILD_COST        = 0.05
    COMMUNICATE_COST  = 0.0000001
    META_INVENT_COST  = 0.10
    COMPOSE_COST      = 0.05
    TRADE_COST        = 0.005
    PUNISH_COST       = 0.08

    def __init__(
        self,
        agent_id      : Optional[str] = None,
        x             : int  = 0,
        y             : int  = 0,
        world_size    : int  = 60,
        seed          : int  = None,
        parent_ids    : Optional[List[str]] = None,
        generation    : int  = 0,
    ):
        self.id           = agent_id or str(uuid.uuid4())[:8]
        self.x            = int(x)
        self.y            = int(y)
        self.world_size   = world_size
        self.parent_ids   = parent_ids or []
        self.generation   = generation
        self.rng          = np.random.RandomState(
            (seed or np.random.randint(0, 2**30)) % (2**31)
        )

        # ── Soul (immutable) ─────────────────────────────────────────────
        self.soul_freqs = self._forge_soul()

        # ── Brain (includes meta-consciousness) ──────────────────────────
        self.brain = HarmonicResonanceConsciousness(
            self.soul_freqs, seed=self.rng.randint(0, 2**31)
        )

        # ── Shortcut to meta layer ───────────────────────────────────────
        self.meta = self.brain.meta

        # ── Body ─────────────────────────────────────────────────────────
        self.energy   = 4.5
        self.health   = 1.0
        self.age      = 0
        self.alive    = True

        # ── Social (original) ───────────────────────────────────────────
        self.tribe_id        : Optional[str] = None
        self.reputation      : float         = 0.0
        self.n_kills         : int           = 0
        self.n_children      : int           = 0

        # ── Action state ─────────────────────────────────────────────────
        self.last_action         : str  = "born"
        self.last_action_success : bool = True
        self.action_counts       : Dict[str, int] = {}

        # ── Knowledge ────────────────────────────────────────────────────
        self.tools               : List[str] = []
        self.absorbed_inventions : List[str] = []

        # ══════════════════════════════════════════════════════════════════
        # NEW v3.0: Inventory Economy (Red/Green/Blue tokens)
        # ══════════════════════════════════════════════════════════════════
        self.inventory : List[int] = [0, 0, 0]

        # ══════════════════════════════════════════════════════════════════
        # NEW v3.0: Role / Caste System
        # ══════════════════════════════════════════════════════════════════
        self.caste_gene   = self.rng.rand(4)  # [Forager, Processor, Warrior, Queen]
        self.role         : str       = "Generalist"
        self.role_history : List[str] = []
        self.is_fertile   : bool      = True if generation == 0 else (self.rng.random() < 0.2)

        # ══════════════════════════════════════════════════════════════════
        # NEW v3.0: Social Trust Memory
        # ══════════════════════════════════════════════════════════════════
        self.social_memory : Dict[str, float] = {}

        # ══════════════════════════════════════════════════════════════════
        # NEW v3.0: Causal Bayesian Model — P(R|do(A))
        # ══════════════════════════════════════════════════════════════════
        self.causal_model : Dict[str, Dict[str, int]] = {}

        # ══════════════════════════════════════════════════════════════════
        # NEW v3.0: Kuramoto Phase Synchronization
        # ══════════════════════════════════════════════════════════════════
        self.kuramoto_phase     : float = self.rng.random() * 2 * np.pi
        self.natural_frequency  : float = 1.0 + self.rng.randn() * 0.1
        self.coupling_strength  : float = 0.5

        # ══════════════════════════════════════════════════════════════════
        # NEW v3.0: Circadian Internal Phase
        # ══════════════════════════════════════════════════════════════════
        self.internal_phase : float = self.rng.random() * 2 * np.pi

        # ══════════════════════════════════════════════════════════════════
        # NEW v3.0: Weather Vote
        # ══════════════════════════════════════════════════════════════════
        self.weather_vote : float = 0.0

        # ══════════════════════════════════════════════════════════════════
        # NEW v3.0: GoL Scratchpad (Turing-complete internal computation)
        # ══════════════════════════════════════════════════════════════════
        self.scratchpad       = np.zeros((32, 32), dtype=np.int8)
        self.scratchpad_writes: int = 0

        # ══════════════════════════════════════════════════════════════════
        # NEW v3.0: Viral Gene Transfer (H-eigenvalue meme packets)
        # ══════════════════════════════════════════════════════════════════
        self.meme_pool : List[dict] = []

        # ══════════════════════════════════════════════════════════════════
        # NEW v3.0: Trade / Punish counters
        # ══════════════════════════════════════════════════════════════════
        self.trade_count  : int = 0
        self.punish_count : int = 0

        # ══════════════════════════════════════════════════════════════════
        # NEW v3.0: Consciousness state mirrors (from brain)
        # ══════════════════════════════════════════════════════════════════
        self.phi_value          : float = 0.0
        self.strange_loop_active: bool  = False

    # ── Soul generation ──────────────────────────────────────────────────────

    def _forge_soul(self) -> np.ndarray:
        phases     = self.rng.uniform(0, 2 * np.pi, K_DIM)
        amplitudes = self.rng.exponential(1.0, K_DIM) + 0.1
        return _BASE_FREQS * np.cos(phases) * amplitudes

    # ── Perception (expanded) ────────────────────────────────────────────────

    def sense(self, world) -> np.ndarray:
        """
        Build sensory observation vector (expanded for v3.0):
          - Local resource gradients (5×5 sparse sample)
          - Own vitals
          - Social density
          - Knowledge field
          - Meta eigenspread
          - Pheromone channels (8)        [NEW]
          - Meme grid channels (3)        [NEW]
          - Season + circadian (3)        [NEW]
          - Social trust average (1)      [NEW]
          - Inventory state (3)           [NEW]
          - Role encoding (1)             [NEW]
        """
        obs = []

        # Local resource field (sparse 5×5 sample)
        for dx in (-4, -2, 0, 2, 4):
            for dy in (-4, -2, 0, 2, 4):
                nx = (self.x + dx) % self.world_size
                ny = (self.y + dy) % self.world_size
                obs.extend(world.resources[nx, ny].tolist())

        # Own vitals
        obs += [
            self.energy / 10.0,
            self.health,
            self.age / self.MAX_AGE,
            self.reputation / 10.0,
            len(self.brain.discoveries) / 20.0,
        ]

        # Social density
        nearby_count = len(world.get_agents_near(self.x, self.y, radius=5))
        obs.append(nearby_count / 15.0)

        # Knowledge field
        obs.append(world.get_knowledge_field(self.x, self.y))

        # Meta eigenspread
        obs.append(self.meta.eigenspread() / 5.0)

        # ── NEW: Pheromone channels (8) ──────────────────────────────────
        pheromone = world.get_pheromone(self.x, self.y)
        obs.extend(pheromone.tolist())

        # ── NEW: Meme grid channels (3) ──────────────────────────────────
        meme = world.get_meme(self.x, self.y)
        obs.extend(meme.tolist())

        # ── NEW: Season + circadian (3) ──────────────────────────────────
        obs.append(float(world.season % 2))               # 0=Summer, 1=Winter
        obs.append(float(np.sin(self.internal_phase)))     # Circadian sin
        obs.append(float(np.cos(self.internal_phase)))     # Circadian cos

        # ── NEW: Social trust average (1) ────────────────────────────────
        if self.social_memory:
            obs.append(float(np.clip(
                np.mean(list(self.social_memory.values())), -1, 1
            )))
        else:
            obs.append(0.0)

        # ── NEW: Inventory state (3) ─────────────────────────────────────
        obs.extend([min(v, 5) / 5.0 for v in self.inventory])

        # ── NEW: Role encoding (1) ───────────────────────────────────────
        role_map = {
            "Generalist": 0.0, "Forager": 0.25,
            "Processor": 0.5, "Warrior": 0.75, "Queen": 1.0
        }
        obs.append(role_map.get(self.role, 0.0))

        return np.array(obs, dtype=float)

    # ── Main step ────────────────────────────────────────────────────────────

    def step(self, world, all_agents: Dict[str, 'BioHyperAgent']
             ) -> Optional['BioHyperAgent']:
        """
        One life tick. Returns a child if reproduction occurs, else None.

        N-tick staggered execution:
          Every tick:  sense, decide, act, learn, evolve, causal update
          Every 5:     Kuramoto phase update
          Every 10:    role update, GoL scratchpad step
          Every 20:    meme absorption
          Every 50:    viral meme broadcast
        """
        if not self.alive:
            return None

        self.age    += 1
        self.energy -= self.BASE_METABOLISM

        # ── Circadian synchronisation ────────────────────────────────────
        self.internal_phase += 0.1 * np.sin(
            world.env_phase - self.internal_phase
        )

        # Sensory input
        sensory = self.sense(world)

        # Decide (Born-rule quantum decision, meta-modulated)
        action, confidence = self.brain.decide(sensory)

        # Cognitive-mode bias (40% chance to override toward dominant mode)
        action = self._mode_bias(action)

        # Execute and collect reward
        reward, child = self._execute(action, world, all_agents)

        # Learn from outcome (meta-modulated) + get Landauer cost
        landauer_cost = self.brain.learn(reward)
        if landauer_cost:
            self.energy -= landauer_cost * 0.5  # Thermodynamic cost of thinking

        self.brain.evolve()

        # ── Causal model update ──────────────────────────────────────────
        sign = "positive" if reward > 0 else "negative"
        if action not in self.causal_model:
            self.causal_model[action] = {"positive": 0, "negative": 0}
        self.causal_model[action][sign] += 1

        # ── IQ complexity bonus ──────────────────────────────────────────
        psi_std = float(np.std(np.abs(self.brain.psi)))
        self.energy += psi_std * 0.01  # Small bonus for cognitive diversity

        # ── Sync consciousness state ─────────────────────────────────────
        self.phi_value           = self.brain.phi_value
        self.strange_loop_active = self.brain.strange_loop_active

        # Log
        self.last_action         = action
        self.last_action_success = (reward >= 0)
        self.action_counts[action] = self.action_counts.get(action, 0) + 1

        # ── Staggered N-tick updates ─────────────────────────────────────

        # Kuramoto phase update (every 5 ticks)
        if self.age % 5 == 0:
            nearby = [a for a in world.get_agents_near(
                self.x, self.y, radius=3
            ) if a.id != self.id and a.alive]
            self.kuramoto_update(nearby)

        # Role update (every 10 ticks)
        if self.age % 10 == 0:
            self.update_role()

        # GoL scratchpad step (every 10 ticks, energy-gated)
        if self.age % 10 == 5 and self.energy > 5.0:
            self.run_gol_step()

        # Meme absorption (every 20 ticks)
        if self.age % 20 == 0 and self.meme_pool:
            self._absorb_meme()

        # Viral meme broadcast (every 50 ticks, energy-gated)
        if self.age % 50 == 0 and self.energy > 7.0:
            self._broadcast_meme(world)

        # Death check
        if self.energy <= 0 or self.health <= 0 or self.age >= self.MAX_AGE:
            self.die(world, all_agents)

        return child

    # ── Mode biasing ─────────────────────────────────────────────────────────

    def _mode_bias(self, base: str) -> str:
        BIAS = {
            CognitionMode.EXPLORE   : ["move_N","move_S","move_E","move_W",
                                        "move_NE","move_NW","move_SE","move_SW"],
            CognitionMode.SURVIVE   : ["eat","rest"],
            CognitionMode.SOCIALIZE : ["communicate","trade","rest"],
            CognitionMode.INVENT    : ["invent","absorb_artifact","meta_invent",
                                        "compose_action"],
            CognitionMode.REPRODUCE : ["reproduce","communicate"],
            CognitionMode.DOMINATE  : ["attack","punish",
                                        "move_N","move_S","move_E","move_W"],
            CognitionMode.MEDITATE  : ["rest","meta_invent","compose_action"],
        }
        mode    = self.brain.get_dominant_mode()
        options = BIAS.get(mode, [])
        if options and self.rng.random() < 0.38:
            return self.rng.choice(options)
        return base

    # ── Action dispatch ──────────────────────────────────────────────────────

    def _execute(self, action: str, world, all_agents: Dict
                 ) -> Tuple[float, Optional['BioHyperAgent']]:
        child = None
        try:
            if   action.startswith("move_"):   reward = self._move(action, world)
            elif action == "eat":              reward = self._eat(world)
            elif action == "attack":           reward = self._attack(world, all_agents)
            elif action == "communicate":      reward = self._communicate(world, all_agents)
            elif action == "reproduce":        reward, child = self._reproduce(world, all_agents)
            elif action == "invent":           reward = self._invent(world)
            elif action == "rest":             reward = self._rest(world)
            elif action == "build_artifact":   reward = self._build_artifact(world)
            elif action == "absorb_artifact":  reward = self._absorb_artifact(world)
            elif action == "meta_invent":      reward = self._meta_invent(world)
            elif action == "compose_action":   reward = self._compose_action(world)
            elif action == "trade":            reward = self._trade(world, all_agents)
            elif action == "punish":           reward = self._punish(world, all_agents)
            else:                              reward = 0.0
        except Exception:
            reward = -0.05
        return reward, child

    # ── Individual actions ────────────────────────────────────────────────────

    _DIR = {
        "move_N": (0,-1), "move_S": (0,1), "move_E": (1,0), "move_W": (-1,0),
        "move_NE":(1,-1), "move_NW":(-1,-1),"move_SE":(1,1), "move_SW":(-1,1),
    }

    def _move(self, direction: str, world) -> float:
        dx, dy   = self._DIR[direction]
        self.x   = (self.x + dx) % self.world_size
        self.y   = (self.y + dy) % self.world_size
        self.energy -= self.MOVE_COST
        local_res    = float(world.resources[self.x, self.y].sum())
        art_bonus = 0.1 if world.get_artifact(self.x, self.y) else 0.0
        kf_bonus = world.get_knowledge_field(self.x, self.y) * 0.05
        # Pheromone attraction bonus
        pheromone = world.get_pheromone(self.x, self.y)
        phero_bonus = float(pheromone.sum()) * 0.02
        # Meme avoidance (danger channel)
        meme = world.get_meme(self.x, self.y)
        danger_penalty = -meme[0] * 0.05
        return local_res * 0.04 - 0.01 + art_bonus + kf_bonus + phero_bonus + danger_penalty

    def _eat(self, world) -> float:
        eaten = 0.0
        for r_type in range(3):   # 3 token types
            consumed = world.consume_resource(self.x, self.y, r_type, 1.2)
            if consumed > 0.1:
                self.inventory[r_type] = min(5, self.inventory[r_type] + 1)
            eaten += consumed
        # Rare element (type 3) - direct energy
        consumed_rare = world.consume_resource(self.x, self.y, 3, 0.8)
        eaten += consumed_rare

        gain = eaten * 1.5
        # Role bonus
        if self.role == "Forager":
            gain *= 1.2
        elif self.role == "Processor" and any(v > 0 for v in self.inventory):
            gain *= 1.5

        self.energy = min(10.0, self.energy + gain)
        self.health = min(1.0,  self.health + eaten * 0.1)

        # Synergy bonus: complete set (1 of each)
        if all(v > 0 for v in self.inventory):
            self.energy = min(10.0, self.energy + 1.5)
            for i in range(3):
                self.inventory[i] -= 1

        # Deposit "resource found" meme
        if eaten > 0.5:
            world.deposit_meme(self.x, self.y, 1, 0.3, tradition_id=hash(self.tribe_id or self.id))


        return gain + 0.02

    def _attack(self, world, all_agents: Dict) -> float:
        nearby = [a for a in world.get_agents_near(self.x, self.y, radius=2)
                  if a.id != self.id and a.alive]
        if not nearby:
            self.energy -= 0.06
            return -0.12

        self.energy -= self.ATTACK_COST
        target       = self.rng.choice(nearby)
        damage       = 0.13 + self.rng.random() * 0.09

        # Shield from bonds
        bonded_partners = world.get_bonded_partners(target.id)
        if bonded_partners:
            shield = min(0.5, len(bonded_partners) * 0.1)
            damage *= (1.0 - shield)

        target.health -= damage
        target.brain.emotions[E.FEAR]  = min(1.0, target.brain.emotions[E.FEAR]  + 0.45)
        target.brain.emotions[E.ANGER] = min(1.0, target.brain.emotions[E.ANGER] + 0.05)

        # Social trust destruction
        target.social_memory[self.id] = target.social_memory.get(self.id, 0) - 1.0

        # Deposit danger meme
        world.deposit_meme(self.x, self.y, 0, 0.5, tradition_id=hash(self.tribe_id or self.id))


        if target.health <= 0:
            target.alive = False
            target.die(world)
            self.n_kills   += 1
            self.reputation -= 2.0
            loot = target.energy * 0.20
            self.energy = min(10.0, self.energy + loot)
            return 0.15

        self.reputation -= 0.50
        return -0.05

    def _communicate(self, world, all_agents: Dict) -> float:
        nearby = [a for a in world.get_agents_near(self.x, self.y, radius=5)
                  if a.id != self.id and a.alive]
        if not nearby:
            return -0.02
        self.energy -= self.COMMUNICATE_COST

        partner  = max(nearby[:8], key=lambda a: self.brain.resonate(a.brain))
        coupling = self.brain.resonate(partner.brain)

        # Bidirectional wave exchange
        self.brain.receive(partner.brain.transmit(), coupling)
        partner.brain.receive(self.brain.transmit(), coupling)

        # Theory of Mind update
        self.brain.model_other(partner.id, partner.brain.transmit())

        # Knowledge diffusion — share one random discovery
        if self.brain.discoveries:
            disc = self.rng.choice(list(self.brain.discoveries.values()))
            if disc['name'] not in partner.absorbed_inventions:
                partner.absorbed_inventions.append(disc['name'])
                partner.brain.emotions[E.WONDER] = min(
                    1.0, partner.brain.emotions[E.WONDER] + 0.15
                )
                self.brain.emotions[E.JOY] = min(1.0, self.brain.emotions[E.JOY] + 0.15)

        # Social trust and bonding
        if coupling > 0.30:
            self.social_memory[partner.id] = self.social_memory.get(partner.id, 0) + 0.1
            partner.social_memory[self.id] = partner.social_memory.get(self.id, 0) + 0.1
            self.reputation    += 0.15
            partner.reputation += 0.15
            # Form bond if high coupling
            if coupling > 0.50:
                world.form_bond(self.id, partner.id)

        # Pheromone deposit (soul-modulated)
        phero_sig = np.abs(self.brain.psi[:8]) * self.soul_freqs[:8]
        phero_max = phero_sig.max() + 1e-12
        world.deposit_pheromone(self.x, self.y, phero_sig / phero_max * 0.3)

        return coupling * 0.50 + 0.10

    def _reproduce(self, world, all_agents: Dict
                   ) -> Tuple[float, Optional['BioHyperAgent']]:
        # Population-adaptive cost (Malthusian scaling)
        n_pop = len([a for a in all_agents.values() if a.alive])
        adaptive_cost = self.REPRODUCE_COST * (1.0 + 0.5 * (n_pop / 128.0) ** 2)

        if self.energy < adaptive_cost:
            return -0.01, None

        # Eusociality: only fertile agents reproduce when pop is high
        if not self.is_fertile and n_pop > 50:
            return 0.01, None

        nearby = [a for a in world.get_agents_near(self.x, self.y, radius=12)
                  if a.id != self.id and a.alive and a.energy > 0.5]
        if not nearby:
            return 0.05, None

        # Prefer high-trust + high-coupling partners
        def partner_score(a):
            coupling = self.brain.resonate(a.brain)
            trust = self.social_memory.get(a.id, 0.0)
            return coupling + trust * 0.2

        partner  = max(nearby, key=partner_score)
        coupling = self.brain.resonate(partner.brain)
        if coupling < 0.01:
            return 0.05, None

        self.energy    -= adaptive_cost
        partner.energy -= adaptive_cost * 0.45

        # Spawn child with epigenetic ψ inheritance
        child_H, child_soul, child_psi = self.brain.spawn_child_H(partner.brain)

        cx = (self.x + self.rng.randint(-2, 3)) % self.world_size
        cy = (self.y + self.rng.randint(-2, 3)) % self.world_size

        child = BioHyperAgent(
            x=cx, y=cy,
            world_size=self.world_size,
            seed=self.rng.randint(0, 2**31),
            parent_ids=[self.id, partner.id],
            generation=max(self.generation, partner.generation) + 1,
        )
        child.soul_freqs = child_soul
        child.brain      = HarmonicResonanceConsciousness(
            child_soul, seed=self.rng.randint(0, 2**31)
        )
        child.brain.H    = child_H
        child.brain._recache()

        # Epigenetic ψ inheritance
        child.brain.psi = child_psi

        # Meta-H inheritance (60/40)
        child_meta_H, child_lr = MetaConsciousness.spawn_child_meta(
            self.meta, partner.meta, self.rng
        )
        child.brain.meta.meta_H   = child_meta_H
        child.brain.meta.lr_field = child_lr
        child.brain.meta._recache_meta()
        child.meta = child.brain.meta

        # Caste gene inheritance (blended + mutation)
        alpha = self.rng.uniform(0.35, 0.65)
        child.caste_gene = np.clip(
            alpha * self.caste_gene + (1 - alpha) * partner.caste_gene
            + self.rng.randn(4) * 0.05, 0, 1
        )
        child.is_fertile = self.rng.random() < 0.2 if child.generation > 0 else True

        child.energy = 2.2

        # Inherit up to 2 discoveries
        for name, disc in list(self.brain.discoveries.items())[:2]:
            child.brain.discoveries[name] = disc
            child.absorbed_inventions.append(name)

        self.n_children += 1
        self.brain.emotions[E.JOY] = min(1.0, self.brain.emotions[E.JOY] + 0.48)
        self.brain.emotions[E.AFFECTION] = min(1.0, self.brain.emotions[E.AFFECTION] + 0.40)
        partner.brain.emotions[E.JOY] = min(1.0, partner.brain.emotions[E.JOY] + 0.48)
        partner.brain.emotions[E.AFFECTION] = min(1.0, partner.brain.emotions[E.AFFECTION] + 0.40)

        # Deposit sacred meme at birth site
        world.deposit_meme(cx, cy, 2, 0.4, tradition_id=hash(self.tribe_id or self.id))


        return coupling * 0.85 + 0.20, child

    def _invent(self, world) -> float:
        if self.energy < self.INVENT_COST:
            return -0.06
        self.energy -= self.INVENT_COST

        # Role bonus for invention
        if self.role == "Processor":
            self.brain.emotions[E.WONDER] = min(
                1.0, self.brain.emotions[E.WONDER] + 0.10
            )

        inv = self.brain.attempt_invention()
        if inv is None:
            return -0.12
        world.place_artifact(self.x, self.y, {
            **inv,
            'creator'  : self.id,
            'step'     : world.step_count,
        })
        world.boost_knowledge_field(self.x, self.y, 1.5)
        # Deposit sacred meme at invention site
        world.deposit_meme(self.x, self.y, 2, 0.5, tradition_id=hash(self.tribe_id or self.id))

        self.brain.emotions[E.WONDER] = min(1.0, self.brain.emotions[E.WONDER] + 0.50)
        return 1.45

    def _rest(self, world=None) -> float:
        gain        = 0.22
        self.energy = min(10.0, self.energy + gain)
        self.health = min(1.0,  self.health + 0.018)
        self.brain.emotions *= 0.97

        # Weather vote based on wonder
        if world and hasattr(world, 'env_phase'):
            self.weather_vote = float(self.brain.emotions[E.WONDER]) * 0.5

        # Seed GoL scratchpad if wondering
        if self.brain.emotions[E.WONDER] > 0.6 and self.energy > 5.0:
            sx = int(self.x) % 32
            sy = int(self.y) % 32
            self.write_scratchpad(sx, sy, 1)

        return 0.04

    def _build_artifact(self, world) -> float:
        if self.energy < self.BUILD_COST:
            return -0.08
        res = world.resources[self.x, self.y].sum()
        if res < 0.4:
            return -0.05
        self.energy -= self.BUILD_COST
        consumed = world.consume_resource(self.x, self.y, 3, 0.25)

        # Decide structure type based on role
        if self.role == "Warrior" and self.rng.random() < 0.5:
            world.add_structure(self.x, self.y, "trap", self.id)
            return 0.35
        elif self.role == "Processor" and self.rng.random() < 0.5:
            world.add_structure(self.x, self.y, "battery", self.id)
            return 0.35
        elif self.role == "Forager" and self.rng.random() < 0.5:
            world.add_structure(self.x, self.y, "cultivator", self.id)
            return 0.40

        name     = f"Tool_{self.id}_{self.age}"
        world.place_artifact(self.x, self.y, {
            'name'      : name,
            'type'      : 'tool',
            'creator'   : self.id,
            'step'      : world.step_count,
            'signature' : float(consumed * 1000),
            'godel'     : GODEL.encode(['focus', 'store']),
            'program'   : ['focus', 'store'],
            'wonder'    : 0.0,
            'diversity' : 0.25,
        })
        self.tools.append(name)
        return 0.30

    def _absorb_artifact(self, world) -> float:
        art = world.get_artifact(self.x, self.y)
        if art is None or art.get('creator') == self.id:
            return -0.02
        if art['name'] not in self.absorbed_inventions:
            self.absorbed_inventions.append(art['name'])
            self.brain.emotions[E.WONDER]    = min(1.0, self.brain.emotions[E.WONDER]    + 0.10)
            self.brain.emotions[E.CURIOSITY] = min(1.0, self.brain.emotions[E.CURIOSITY] + 0.05)
            return 0.42
        return 0.01

    # ── NEW: Meta-invent ─────────────────────────────────────────────────────

    def _meta_invent(self, world) -> float:
        if self.energy < self.META_INVENT_COST:
            return -0.10
        self.energy -= self.META_INVENT_COST
        result = self.brain.attempt_meta_invention()
        if result is None:
            return -0.15
        world.boost_knowledge_field(self.x, self.y, 2.0)
        self.brain.emotions[E.WONDER] = min(1.0, self.brain.emotions[E.WONDER] + 0.60)
        return 1.85

    # ── NEW: Compose action ──────────────────────────────────────────────────

    def _compose_action(self, world) -> float:
        if self.energy < self.COMPOSE_COST:
            return -0.05
        self.energy -= self.COMPOSE_COST
        result = self.brain.compose_new_action()
        if result is None:
            return -0.08
        world.place_artifact(self.x, self.y, {
            **result,
            'type'      : 'ideology',
            'creator'   : self.id,
            'step'      : world.step_count,
            'signature' : float(result['godel']),
            'wonder'    : float(self.brain.emotions[E.WONDER]),
        })
        world.boost_knowledge_field(self.x, self.y, 0.3)
        return 0.50

    # ══════════════════════════════════════════════════════════════════════════
    # NEW v3.0: TRADE ACTION
    # ══════════════════════════════════════════════════════════════════════════

    def _trade(self, world, all_agents: Dict) -> float:
        """Exchange inventory tokens with a bonded partner."""
        bonded = world.get_bonded_partners(self.id)
        if not bonded:
            return -0.02

        self.energy -= self.TRADE_COST

        for pid in bonded:
            partner = all_agents.get(pid)
            if not partner or not partner.alive:
                continue
            # Look for complementary tokens to trade
            for i in range(3):
                for j in range(3):
                    if i != j and self.inventory[i] > 0 and partner.inventory[j] > 0:
                        self.inventory[i] -= 1
                        self.inventory[j] += 1
                        partner.inventory[j] -= 1
                        partner.inventory[i] += 1
                        self.trade_count  += 1
                        partner.trade_count += 1
                        # Trust boost
                        self.social_memory[pid] = self.social_memory.get(pid, 0) + 0.5
                        partner.social_memory[self.id] = partner.social_memory.get(self.id, 0) + 0.5
                        return 0.40
        return -0.01

    # ══════════════════════════════════════════════════════════════════════════
    # NEW v3.0: PUNISH ACTION
    # ══════════════════════════════════════════════════════════════════════════

    def _punish(self, world, all_agents: Dict) -> float:
        """Costly punishment of defectors. Costs energy, deals damage."""
        nearby = [a for a in world.get_agents_near(self.x, self.y, radius=2)
                  if a.id != self.id and a.alive]
        if not nearby:
            return -0.06

        self.energy -= self.PUNISH_COST

        # Target the agent with worst social trust
        target = min(nearby, key=lambda a: self.social_memory.get(a.id, 0.0))
        damage = 0.15
        target.health -= damage
        target.energy -= 0.10
        target.brain.emotions[E.FEAR] = min(
            1.0, target.brain.emotions[E.FEAR] + 0.30
        )

        # Trust destruction
        target.social_memory[self.id] = target.social_memory.get(self.id, 0) - 1.0

        # Deposit danger meme
        world.deposit_meme(self.x, self.y, 0, 0.4)

        self.punish_count += 1
        self.reputation -= 0.30
        return 0.05

    # ══════════════════════════════════════════════════════════════════════════
    # NEW v3.0: ROLE / CASTE SYSTEM
    # ══════════════════════════════════════════════════════════════════════════

    def update_role(self) -> None:
        """Assign role based on caste genetics + current state."""
        # Queens keep their role unless starving
        if self.role == "Queen" and self.energy > 4.0:
            return

        if self.is_fertile and self.energy > 6.0 and self.age > 50:
            self.role = "Queen"
        elif any(v > 0 for v in self.inventory):
            self.role = "Processor"
        elif self.caste_gene[2] > 0.6 and self.energy > 5.0:
            self.role = "Warrior"
        elif self.caste_gene[0] > 0.5:
            self.role = "Forager"
        else:
            self.role = "Generalist"

        self.role_history.append(self.role)
        if len(self.role_history) > 100:
            self.role_history.pop(0)

    # ══════════════════════════════════════════════════════════════════════════
    # NEW v3.0: KURAMOTO PHASE SYNCHRONIZATION
    # ══════════════════════════════════════════════════════════════════════════

    def kuramoto_update(self, neighbors: list) -> None:
        """
        Kuramoto model: dθ/dt = ω + (K/N)Σ sin(θⱼ - θᵢ)
        """
        if not neighbors:
            return
        phase_diff_sum = sum(
            np.sin(getattr(n, 'kuramoto_phase', 0) - self.kuramoto_phase)
            for n in neighbors
        )
        n_count = len(neighbors)
        d_theta = (self.natural_frequency
                   + (self.coupling_strength / n_count) * phase_diff_sum)
        self.kuramoto_phase = (self.kuramoto_phase + d_theta * 0.1) % (2 * np.pi)

    # ══════════════════════════════════════════════════════════════════════════
    # NEW v3.0: GOL SCRATCHPAD (Turing-complete internal computation)
    # ══════════════════════════════════════════════════════════════════════════

    def run_gol_step(self) -> None:
        """One step of Conway's Game of Life on the internal scratchpad."""
        pad = self.scratchpad
        neighbors = (
            np.roll(np.roll(pad, 1, 0), 1, 1) + np.roll(np.roll(pad, 1, 0), -1, 1) +
            np.roll(np.roll(pad, -1, 0), 1, 1) + np.roll(np.roll(pad, -1, 0), -1, 1) +
            np.roll(pad, 1, 0) + np.roll(pad, -1, 0) +
            np.roll(pad, 1, 1) + np.roll(pad, -1, 1)
        )
        birth   = (neighbors == 3) & (pad == 0)
        survive = ((neighbors == 2) | (neighbors == 3)) & (pad == 1)
        self.scratchpad = (birth | survive).astype(np.int8)

    def write_scratchpad(self, x: int, y: int, value: int) -> None:
        if 0 <= x < 32 and 0 <= y < 32:
            self.scratchpad[x, y] = 1 if value else 0
            self.scratchpad_writes += 1

    # ══════════════════════════════════════════════════════════════════════════
    # NEW v3.0: VIRAL GENE TRANSFER (H-eigenvalue meme packets)
    # ══════════════════════════════════════════════════════════════════════════

    def _broadcast_meme(self, world) -> None:
        """Create cognitive virus packet from H eigenvalues."""
        packet = {
            'eigenvals'    : self.brain._evals[:8].copy(),
            'fitness'      : self.energy,
            'soul_fragment': self.soul_freqs[:8].copy(),
            'sender'       : self.id,
        }
        nearby = world.get_agents_near(self.x, self.y, radius=3)
        for n in nearby:
            if n.id != self.id and len(getattr(n, 'meme_pool', [])) < 5:
                n.meme_pool.append(packet)

    def _absorb_meme(self) -> None:
        """Absorb the fittest meme from pool: blend H eigenvalues."""
        if not self.meme_pool:
            return
        best = max(self.meme_pool, key=lambda m: m['fitness'])
        self.meme_pool.clear()

        eigenvals = best['eigenvals']
        n = min(len(eigenvals), K_DIM)
        for i in range(n):
            self.brain.H[i, i] = self.brain.H[i, i] * 0.97 + eigenvals[i] * 0.03
        self.brain.H = (self.brain.H + self.brain.H.conj().T) / 2
        self.brain._recache()

    # ── Death (with apoptotic information transfer) ──────────────────────────

    def die(self, world, all_agents=None) -> None:
        """
        Death with apoptotic information transfer.
        Broadcasts spectral fingerprint + top discoveries to nearby agents.
        """
        self.alive = False

        # Legacy artifact
        if self.brain.discoveries:
            legacy = list(self.brain.discoveries.values())[-1]
            world.place_artifact(self.x, self.y, {
                **legacy,
                'creator'  : self.id,
                'type'     : 'legacy',
                'step'     : world.step_count,
            })

        # Apoptotic death packet
        if all_agents:
            death_packet = {
                'spectral_fingerprint': self.brain._evals[:K_META].copy(),
                'meta_H_fragment'     : self.brain.meta.meta_H[:8, :8].copy(),
                'top_discoveries'     : list(self.brain.discoveries.keys())[-3:],
                'soul_fragment'       : self.soul_freqs[:8].copy(),
                'role'                : self.role,
                'causal_model'        : dict(list(self.causal_model.items())[:5]),
            }
            nearby = [a for a in world.get_agents_near(self.x, self.y, radius=4)
                      if a.id != self.id and a.alive]
            for neighbor in nearby:
                neighbor._receive_death_wisdom(death_packet)

    def _receive_death_wisdom(self, packet: dict) -> None:
        """Absorb wisdom from a dying agent. Blend H eigenvalues + causal knowledge."""
        fingerprint = packet.get('spectral_fingerprint')
        if fingerprint is not None:
            n = min(len(fingerprint), K_META)
            for i in range(n):
                self.brain.H[i, i] = self.brain.H[i, i] * 0.97 + fingerprint[i] * 0.03
            self.brain.H = (self.brain.H + self.brain.H.conj().T) / 2
            self.brain._recache()

        # Inherit causal knowledge
        for action, counts in packet.get('causal_model', {}).items():
            if action not in self.causal_model:
                self.causal_model[action] = {"positive": 0, "negative": 0}
            for sign, val in counts.items():
                self.causal_model[action][sign] += max(0, val // 3)

    # ── Serialisation ────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        rgb = self.brain.spectral_rgb()
        return {
            'id'              : self.id,
            'x'               : self.x,
            'y'               : self.y,
            'energy'          : round(float(self.energy), 2),
            'health'          : round(float(self.health), 3),
            'age'             : int(self.age),
            'alive'           : self.alive,
            'generation'      : self.generation,
            'tribe'           : self.tribe_id or 'Nomad',
            'mode'            : self.brain.get_dominant_mode().value,
            'last_action'     : self.last_action,
            'reputation'      : round(float(self.reputation), 2),
            'inventions'      : len(self.brain.discoveries),
            'absorbed'        : len(self.absorbed_inventions),
            'kills'           : self.n_kills,
            'children'        : self.n_children,
            'color'           : f'rgb({rgb[0]},{rgb[1]},{rgb[2]})',
            'r'               : rgb[0],
            'g'               : rgb[1],
            'b'               : rgb[2],
            'curiosity'       : round(float(self.brain.emotions[E.CURIOSITY]), 2),
            'wonder'          : round(float(self.brain.emotions[E.WONDER]), 2),
            'fear'            : round(float(self.brain.emotions[E.FEAR]), 2),
            'meta_eigenspread': round(float(self.meta.eigenspread()), 3),
            'meta_inventions' : self.meta.n_meta_inventions,
            'composed_actions': len(self.brain.composed_actions),
            # ── NEW v3.0 fields ──────────────────────────────────────────
            'role'            : self.role,
            'inventory'       : list(self.inventory),
            'phi'             : round(float(self.phi_value), 3),
            'strange_loop'    : self.strange_loop_active,
            'kuramoto_phase'  : round(float(self.kuramoto_phase), 3),
            'trade_count'     : self.trade_count,
            'punish_count'    : self.punish_count,
            'n_bonds'         : len(self.social_memory),
            'scratchpad_writes': self.scratchpad_writes,
            'tom_depth'       : self.brain.tom_depth,
            'qualia'          : self.brain.classify_qualia(),
        }
