// 纯卷号规则：精确列举 Python str.strip 空白，校验副本但保存原值。
using System.Buffers;
using System.Text;
namespace AIIS.Backend.app.Plan.Domain;

public static class PlanRules
{
    private static bool PythonWhitespace(char c) => c is >= '\u0009' and <= '\u000d' or >= '\u001c' and <= '\u0020' or '\u0085' or '\u00a0' or '\u1680' or >= '\u2000' and <= '\u200a' or '\u2028' or '\u2029' or '\u202f' or '\u205f' or '\u3000';
    public static string Strip(string value)
    {
        int start = 0, end = value.Length;
        while (start < end && PythonWhitespace(value[start])) start++;
        while (end > start && PythonWhitespace(value[end - 1])) end--;
        return value[start..end];
    }
    public static bool ValidCoil(string value)
    {
        var copy = Strip(value);
        return copy.Length > 0 && !copy.Any(c => c <= '\u001f' || c == '\u007f');
    }
    public static int ScalarLength(string value)
    {
        int length = 0;
        var span = value.AsSpan();
        while (!span.IsEmpty)
        {
            if (Rune.DecodeFromUtf16(span, out _, out int consumed) != OperationStatus.Done) return -1;
            length++;
            span = span[consumed..];
        }
        return length;
    }
}
