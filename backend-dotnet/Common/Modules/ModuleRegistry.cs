// 静态模块组合只校验元数据；重复 ID、缺依赖、路由冲突启动失败。
namespace AIIS.Backend.Common.Modules;

public sealed record ModuleDefinition(string Id, bool Enabled, IReadOnlyList<string> Dependencies, IReadOnlyList<string> Routes, IReadOnlyList<Type> Endpoints, Type Service, Type Entity);
public static class ModuleRegistry
{
    public static IReadOnlyList<ModuleDefinition> Validate(IReadOnlyList<ModuleDefinition> modules)
    {
        var ids = new HashSet<string>(StringComparer.Ordinal);
        var routes = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        foreach (var module in modules)
            if (!ids.Add(module.Id)) throw new InvalidOperationException("module_duplicate_id");
        foreach (var module in modules.Where(x => x.Enabled))
        {
            if (module.Dependencies.Any(id => !modules.Any(x => x.Id == id && x.Enabled))) throw new InvalidOperationException("module_dependency_missing");
            foreach (string route in module.Routes)
                if (!routes.Add(route)) throw new InvalidOperationException("module_route_conflict");
        }
        return modules.Where(x => x.Enabled).ToArray();
    }
}
