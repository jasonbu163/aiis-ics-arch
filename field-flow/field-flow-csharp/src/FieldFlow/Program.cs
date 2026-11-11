// CLI 入口只负责交给命令装配层。
using FieldFlow.Cli;

return await Commands.RunAsync(args);
