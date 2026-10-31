export type Action = {
  font_size: number;
  font_family: string;
  line_spacing: number;
  chunk_size: number | string;
  tts_rate: number | string;
  theme: "light" | "dark" | "cream";
};

export type Persona = {
  id: string;
  label: string;
  split: "training" | "held_out";
  base_wpm: number;
  preferred_action: Action;
  comprehension_bias: number;
  fatigue_rate: number;
  recovery_rate: number;
};

export type Simulator = {
  scope: string;
  presets: Action[];
  preset_names: string[];
  personas: Persona[];
};

export type PresetScore = {
  action_index: number;
  estimate: number;
  exploration_bonus: number | null;
  allowed: boolean;
};

export type StepResponse = {
  preset_scores?: PresetScore[];
  action_index: number;
  action: Action;
  reward: number;
  estimated_value: number;
  exploring: boolean;
  explanation: string;
};
