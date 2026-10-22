//! 五类确定规则：输入模拟时间，不读取UI或wall clock，不拥有第二份image。
use super::typed_value;
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use sha2::{Digest, Sha256};

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum RuleKind {
    Fixed,
    Ramp,
    Sine,
    Random,
    Toggle,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct RuleSpec {
    pub kind: RuleKind,
    #[serde(default)]
    pub fixed_value: Value,
    #[serde(default)]
    pub min: f64,
    #[serde(default = "one")]
    pub max: f64,
    #[serde(default = "period")]
    pub period_ms: u32,
    #[serde(default)]
    pub phase: f64,
    #[serde(default)]
    pub seed: String,
    #[serde(default = "half")]
    pub half_period_ms: u32,
}
fn one() -> f64 {
    1.
}
fn period() -> u32 {
    1000
}
fn half() -> u32 {
    500
}

pub fn validate(kind: &str, rule: &RuleSpec) -> Result<(), String> {
    if rule.period_ms < 100
        || rule.half_period_ms < 100
        || !rule.phase.is_finite()
        || rule.seed.len() > 100
    {
        return Err("rule_parameters".into());
    }
    if rule.kind == RuleKind::Fixed {
        typed_value::encode(kind, &rule.fixed_value)?;
        return Ok(());
    }
    if rule.kind == RuleKind::Toggle {
        return if kind == "BOOL" {
            Ok(())
        } else {
            Err("rule_type".into())
        };
    }
    let (min, max) = typed_value::numeric_bounds(kind).ok_or("rule_type")?;
    if !rule.min.is_finite()
        || !rule.max.is_finite()
        || rule.min > rule.max
        || rule.min < min
        || rule.max > max
    {
        return Err("rule_range".into());
    }
    if kind != "REAL" && (rule.min.fract() != 0. || rule.max.fract() != 0.) {
        return Err("rule_range".into());
    }
    Ok(())
}

pub fn evaluate(
    kind: &str,
    rule: &RuleSpec,
    instance: &str,
    point: &str,
    simulated_ns: u64,
) -> Result<Vec<u8>, String> {
    validate(kind, rule)?;
    if rule.kind == RuleKind::Fixed {
        return typed_value::encode(kind, &rule.fixed_value);
    }
    if rule.kind == RuleKind::Toggle {
        return typed_value::encode(
            kind,
            &json!((simulated_ns / (rule.half_period_ms as u64 * 1_000_000)) % 2 != 0),
        );
    }
    let period_ns = rule.period_ms as u64 * 1_000_000;
    let bucket = simulated_ns / period_ns;
    let value = match rule.kind {
        RuleKind::Ramp => {
            rule.min
                + (rule.max - rule.min) * ((simulated_ns % period_ns) as f64 / period_ns as f64)
        }
        RuleKind::Sine => {
            rule.min
                + (rule.max - rule.min)
                    * (0.5
                        + 0.5
                            * (std::f64::consts::TAU
                                * ((simulated_ns % period_ns) as f64 / period_ns as f64
                                    + rule.phase))
                                .sin())
        }
        RuleKind::Random => {
            let mut h = Sha256::new();
            for field in [instance, point, &rule.seed, &bucket.to_string()] {
                h.update(field.as_bytes());
                h.update([0]);
            }
            let digest = h.finalize();
            if kind == "REAL" {
                let high = u32::from_be_bytes([0, digest[0], digest[1], digest[2]]);
                rule.min + (rule.max - rule.min) * high as f64 / 16777215.
            } else {
                let integer = u64::from_be_bytes(digest[..8].try_into().unwrap());
                rule.min + (integer % ((rule.max - rule.min + 1.) as u64)) as f64
            }
        }
        _ => unreachable!(),
    }
    .clamp(rule.min, rule.max);
    let value = if kind == "REAL" {
        json!(value as f32)
    } else if kind == "BOOL" {
        json!(value.floor() != 0.)
    } else {
        json!(value.floor() as i64)
    };
    typed_value::encode(kind, &value)
}
