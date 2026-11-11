// 停止与发送开始按同一个闸门排序。
namespace FieldFlow.Services;

internal sealed class SendGate
{
    private readonly object sync = new();
    private bool closed;

    public bool IsClosed { get { lock (sync) return closed; } }
    public void Close() { lock (sync) closed = true; }

    public Task Start(Func<Task> send)
    {
        lock (sync)
        {
            if (closed) throw new OperationCanceledException("send_gate_closed");
            return send();
        }
    }
}
