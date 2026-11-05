// 文档适配真实绑定合同：Decimal为number|string，列明手动绑定的分页/过滤参数。
using Microsoft.AspNetCore.OpenApi;
using Microsoft.OpenApi;
namespace AIIS.Backend.Common.Serialization;

public static class PlanOpenApi
{
    public static void Configure(OpenApiOptions options)
    {
        options.AddSchemaTransformer((schema, context, _) =>
        {
            if (context.JsonTypeInfo.Type == typeof(decimal))
            {
                schema.Type = null; schema.Format = null;
                schema.AnyOf = [new OpenApiSchema { Type = JsonSchemaType.Number }, new OpenApiSchema { Type = JsonSchemaType.String }];
            }
            return Task.CompletedTask;
        });
        options.AddOperationTransformer((operation, context, _) =>
        {
            if (context.Description.HttpMethod == "GET" && context.Description.RelativePath == "api/v1/plans")
            {
                operation.Parameters ??= [];
                foreach (string field in new[] { "page", "pageSize", "coilNo", "grade", "materialStatus", "status" })
                    operation.Parameters.Add(new OpenApiParameter { Name = field, In = ParameterLocation.Query, Required = false, Schema = new OpenApiSchema { Type = field is "page" or "pageSize" ? JsonSchemaType.Integer : JsonSchemaType.String } });
            }
            return Task.CompletedTask;
        });
    }
}
