// 原始十进制文本先无损归一化并检查存储边界，绝不先转 double/有损 decimal。
using System.Globalization;
using System.Text.RegularExpressions;
namespace AIIS.Backend.Common.Serialization;

public static partial class ExactDecimal
{
    [GeneratedRegex(@"^[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?$", RegexOptions.CultureInvariant)]
    private static partial Regex Syntax();
    public static bool TryParse(string text, int precision, int scale, out decimal value)
    {
        value = 0;
        text = text.Trim(' ', '\t', '\r', '\n');
        if (!Syntax().IsMatch(text)) return false;
        bool negative = text.StartsWith('-');
        text = text.TrimStart('+', '-');
        var parts = text.Split('e', 'E');
        string significant = parts[0];
        int dot = significant.IndexOf('.');
        long fractional = dot < 0 ? 0 : significant.Length - dot - 1;
        string digits = significant.Replace(".", "").TrimStart('0');
        if (digits.Length == 0) return true;
        if (parts.Length == 2)
        {
            if (!int.TryParse(parts[1], NumberStyles.AllowLeadingSign, CultureInfo.InvariantCulture, out int exponent)) return false;
            fractional -= exponent;
        }
        while (digits.EndsWith('0')) { digits = digits[..^1]; fractional--; }
        if (fractional > scale || digits.Length - fractional > precision - scale) return false;
        if (fractional < 0) digits += new string('0', checked((int)-fractional));
        else if (fractional > 0)
        {
            digits = digits.PadLeft((int)fractional + 1, '0');
            digits = digits.Insert(digits.Length - (int)fractional, ".");
        }
        return decimal.TryParse((negative ? "-" : "") + digits, NumberStyles.AllowLeadingSign | NumberStyles.AllowDecimalPoint, CultureInfo.InvariantCulture, out value);
    }
}
