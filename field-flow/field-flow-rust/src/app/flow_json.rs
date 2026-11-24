//! 文件：src/app/flow_json.rs；执行一轮已校验的只读 HTTP 命令判断。
use crate::{config::flow_json::JsonFlow, services::Http, Result};

pub(crate) async fn iteration(flow: &JsonFlow, http: &Http) -> Result<&'static str> {
    let input = http.get_strict(flow.url.as_str()).await?;
    let ready = input.validated_ready(&flow.source_id, flow.max_age_ms)?;
    Ok(if ready == flow.expected {
        "matched"
    } else {
        "not_matched"
    })
}
