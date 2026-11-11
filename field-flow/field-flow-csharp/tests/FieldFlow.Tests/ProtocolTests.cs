// 用独立 Snap7 既有捕获验证两字节请求与应答关联。
using FieldFlow.Infrastructure.S7;
using Microsoft.VisualStudio.TestTools.UnitTesting;

namespace FieldFlow.Tests;

[TestClass]
public sealed class ProtocolTests
{
    [TestMethod]
    public void Int16FramesMatchIndependentCapture()
    {
        Assert.AreEqual("0300001f02f080320100000001000e00000401120a10020002000184000000",
            Convert.ToHexStringLower(S7Frames.Request(1, 0, 1, null)));
        Assert.AreEqual("0300002502f080320100000001000e00060501120a1002000200018400000000040010002a",
            Convert.ToHexStringLower(S7Frames.Request(1, 0, 1, 42)));
        Assert.AreEqual((short)42, S7Frames.ValidateResponse(
            Convert.FromHexString("0300001b02f0803203000000010002000600000401ff040010002a"), 1, false));
        _ = S7Frames.ValidateResponse(
            Convert.FromHexString("0300001602f0803203000000010002000100000501ff"), 1, true);
    }

    [TestMethod]
    public void WrongReferenceAndTruncationCannotConfirmWrite()
    {
        var wrong = Convert.FromHexString("0300001602f0803203000000020002000100000501ff");
        var shortFrame = Convert.FromHexString("0300001102f08032030000000100020001");
        Assert.ThrowsExactly<IOException>(() => S7Frames.ValidateResponse(wrong, 1, true));
        Assert.ThrowsExactly<IOException>(() => S7Frames.ValidateResponse(shortFrame, 1, true));
    }
}
