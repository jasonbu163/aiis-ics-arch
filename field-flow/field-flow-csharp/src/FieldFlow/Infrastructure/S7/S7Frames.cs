// 有界 S7 DB INT16 帧与应答关联校验。
using System.Buffers.Binary;
using FieldFlow.Domain;

namespace FieldFlow.Infrastructure.S7;

internal static class S7Frames
{
    public static byte[] Connect(Plc plc) =>
    [
        3, 0, 0, 22, 17, 0xe0, 0, 0, 0, 1, 0,
        0xc0, 1, 10, 0xc1, 2, 1, 0,
        0xc2, 2, 1, (byte)(plc.Rack * 32 + plc.Slot)
    ];

    public static readonly byte[] Setup =
        Convert.FromHexString("0300001902F08032010000000000080000F0000001000100F0");

    public static byte[] Request(int db, int offset, ushort reference, short? value)
    {
        var write = value.HasValue;
        var bytes = Convert.FromHexString(write
            ? "0300002502F080320100000000000E00060501120A10020002000084000000000400100000"
            : "0300001F02F080320100000000000E00000401120A10020002000084000000");
        BinaryPrimitives.WriteUInt16BigEndian(bytes.AsSpan(11), reference);
        BinaryPrimitives.WriteUInt16BigEndian(bytes.AsSpan(25), checked((ushort)db));
        var bits = checked(offset * 8);
        bytes[28] = (byte)(bits >> 16);
        bytes[29] = (byte)(bits >> 8);
        bytes[30] = (byte)bits;
        if (write) BinaryPrimitives.WriteInt16BigEndian(bytes.AsSpan(35), value!.Value);
        return bytes;
    }

    public static void ValidateConnect(byte[] frame, Plc plc)
    {
        if (frame.Length != 22 || frame[4] != 17 || frame[5] != 0xd0 ||
            frame[6] != 0 || frame[7] != 1 || frame[10] != 0)
            throw new IOException("s7_connect_response");
        var found = new Dictionary<byte, byte[]>();
        for (var i = 11; i < frame.Length;)
        {
            if (i + 2 > frame.Length) throw new IOException("s7_connect_response");
            var key = frame[i++];
            var length = frame[i++];
            if (i + length > frame.Length || !found.TryAdd(key, frame.AsSpan(i, length).ToArray()))
                throw new IOException("s7_connect_response");
            i += length;
        }
        if (found.Count != 3 || !found.TryGetValue(0xc0, out var size) || !size.SequenceEqual(new byte[] { 10 }) ||
            !found.TryGetValue(0xc1, out var local) || !local.SequenceEqual(new byte[] { 1, 0 }) ||
            !found.TryGetValue(0xc2, out var remote) ||
            !remote.SequenceEqual(new byte[] { 1, (byte)(plc.Rack * 32 + plc.Slot) }))
            throw new IOException("s7_connect_response");
    }

    public static void ValidateSetup(byte[] frame)
    {
        var expected = Convert.FromHexString("0300001B02F080320300000000000800000000F0000001000100F0");
        if (!frame.SequenceEqual(expected)) throw new IOException("s7_setup_response");
    }

    public static short ValidateResponse(byte[] frame, ushort reference, bool write)
    {
        var expected = Convert.FromHexString(write
            ? "0300001602F0803203000000000002000100000501FF"
            : "0300001B02F0803203000000000002000600000401FF0400100000");
        if (frame.Length != expected.Length) throw new IOException("s7_response_length");
        BinaryPrimitives.WriteUInt16BigEndian(expected.AsSpan(11), reference);
        var end = write ? expected.Length : expected.Length - 2;
        if (!frame.AsSpan(0, end).SequenceEqual(expected.AsSpan(0, end)))
            throw new IOException("s7_response_mismatch");
        return write ? (short)0 : BinaryPrimitives.ReadInt16BigEndian(frame.AsSpan(end));
    }
}
