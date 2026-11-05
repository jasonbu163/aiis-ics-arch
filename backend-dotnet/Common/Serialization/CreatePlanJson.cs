// 单一平面创建合同的严格 JSON binder：检测重复键、缺失/null、Unicode 与无损 Decimal。
using System.Globalization;
using System.Reflection;
using System.Text;
using System.Text.Json;
using AIIS.Backend.app.Plan.Contracts;
using AIIS.Backend.app.Plan.Domain;
using AIIS.Backend.app.Plan.Validators;
using AIIS.Backend.Common.Errors;
using FastEndpoints;
namespace AIIS.Backend.Common.Serialization;

public sealed class CreatePlanJson : IRequestBinder<CreatePlanIn>
{
    private static readonly Dictionary<string, PropertyInfo> Properties = typeof(CreatePlanIn).GetProperties().ToDictionary(p => JsonNamingPolicy.CamelCase.ConvertName(p.Name), StringComparer.Ordinal);
    private static readonly string[] Required = ["coilNo", "grade", "spec", "weight", "thickness", "width"];
    public async ValueTask<CreatePlanIn> BindAsync(BinderContext ctx, CancellationToken ct)
    {
        var request = ctx.HttpContext.Request;
        if (!string.Equals(request.ContentType?.Split(';')[0].Trim(), "application/json", StringComparison.OrdinalIgnoreCase)) throw new PlanException(415, "plan_invalid_request");
        using var bytes = new MemoryStream();
        await request.Body.CopyToAsync(bytes, ct);
        return Parse(bytes.ToArray());
    }
    public static CreatePlanIn Parse(byte[] bytes)
    {
        try
        {
            var json = new UTF8Encoding(false, true).GetString(bytes);
            using var doc = JsonDocument.Parse(json, new JsonDocumentOptions { MaxDepth = 8 });
            if (doc.RootElement.ValueKind != JsonValueKind.Object) throw PlanException.Invalid("body", "object_required");
            var input = new CreatePlanIn();
            var seen = new HashSet<string>(StringComparer.Ordinal);
            foreach (var item in doc.RootElement.EnumerateObject())
            {
                if (!seen.Add(item.Name)) throw PlanException.Invalid(item.Name, "duplicate_property");
                if (!Properties.TryGetValue(item.Name, out var property)) throw PlanException.Invalid(item.Name, "unknown_property");
                if (item.Value.ValueKind == JsonValueKind.Null)
                {
                    if (item.Name != "remark") throw PlanException.Invalid(item.Name, "null_not_allowed");
                    continue;
                }
                object value;
                if (property.PropertyType == typeof(string))
                {
                    if (item.Value.ValueKind != JsonValueKind.String) throw PlanException.Invalid(item.Name, "string_required");
                    value = item.Value.GetString()!;
                    if (PlanRules.ScalarLength((string)value) < 0) throw PlanException.Invalid(item.Name, "invalid_unicode");
                }
                else if (property.PropertyType == typeof(int))
                {
                    var raw = item.Value.GetRawText();
                    if (item.Value.ValueKind != JsonValueKind.Number || raw.Any(c => c is not (>= '0' and <= '9') && c != '-') || !item.Value.TryGetInt32(out int number)) throw PlanException.Invalid(item.Name, "integer_required");
                    value = number;
                }
                else
                {
                    if (item.Value.ValueKind is not (JsonValueKind.String or JsonValueKind.Number)) throw PlanException.Invalid(item.Name, "decimal_required");
                    string text = item.Value.ValueKind == JsonValueKind.String ? item.Value.GetString()! : item.Value.GetRawText();
                    int scale = item.Name == "thickness" ? 3 : item.Name == "weight" || item.Name.Contains("UnitTension", StringComparison.Ordinal) ? 4 : 2;
                    int precision = scale == 4 ? 12 : 10;
                    if (!ExactDecimal.TryParse(text, precision, scale, out decimal number)) throw PlanException.Invalid(item.Name, "decimal_precision");
                    value = number;
                }
                property.SetValue(input, value);
            }
            foreach (string field in Required) if (!seen.Contains(field)) throw PlanException.Invalid(field, "required");
            var result = new CreatePlanValidator().Validate(input);
            if (!result.IsValid)
            {
                bool coil = result.Errors.Any(e => e.ErrorCode == "plan_invalid_coil_no");
                throw new PlanException(422, coil ? "plan_invalid_coil_no" : "plan_invalid_request", result.Errors.Select(e => new FieldError(JsonNamingPolicy.CamelCase.ConvertName(e.PropertyName), e.ErrorCode)).ToArray());
            }
            return input;
        }
        catch (Exception ex) when (ex is JsonException or DecoderFallbackException or InvalidOperationException or ArgumentException)
        {
            throw PlanException.Invalid("body", "invalid_json");
        }
    }
}
