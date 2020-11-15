import unittest

import building
from models import bottlenecks, encoders, decoders


class TestBuildingDataModule(unittest.TestCase):
    def test_denoising(self):
        dm = building.build_datamodule('denoising')
        self.assertTrue(dm.apply_noise)

    def test_rest(self):
        rest = ['shallow',
                'vanilla',
                'stacked',
                'sparse',
                'vae',
                'beta_vae_strict',
                'beta_vae_loose',
                'vq']
        for model_type in rest:
            with self.subTest(model_type=model_type):
                dm = building.build_datamodule(model_type)
                self.assertFalse(dm.apply_noise)


class TestBuildingAE(unittest.TestCase):
    def test_build_bottleneck(self):
        with self.subTest(model_type='vanilla'):
            neck = self._build_neck('vanilla')
            self.assertIsInstance(neck, bottlenecks.IdentityBottleneck)
        with self.subTest(model_type='stacked'):
            neck = self._build_neck('stacked')
            self.assertIsInstance(neck, bottlenecks.IdentityBottleneck)
        with self.subTest(model_type='denoising'):
            neck = self._build_neck('denoising')
            self.assertIsInstance(neck, bottlenecks.IdentityBottleneck)
        with self.subTest(model_type='vae'):
            neck = self._build_neck('vae')
            self.assertIsInstance(neck, bottlenecks.VariationalBottleneck)
            self.assertEqual(1., neck.beta)
        with self.subTest(model_type='beta_vae_strict'):
            neck = self._build_neck('beta_vae_strict')
            self.assertIsInstance(neck, bottlenecks.VariationalBottleneck)
            self.assertEqual(2., neck.beta)
        with self.subTest(model_type='beta_vae_loose'):
            neck = self._build_neck('beta_vae_loose')
            self.assertIsInstance(neck, bottlenecks.VariationalBottleneck)
            self.assertEqual(0.5, neck.beta)
        with self.subTest(model_type='sparse'):
            neck = self._build_neck('sparse')
            self.assertIsInstance(neck, bottlenecks.SparseBottleneck)
            self.assertEqual(0.1, neck.sparsity)
            self.assertEqual(1., neck.beta)
        with self.subTest(model_type='vq'):
            neck = self._build_neck('vq')
            self.assertIsInstance(neck, bottlenecks.VectorQuantizedBottleneck)
            self.assertEqual(32, neck.latent_dim)
            self.assertEqual(512, neck.num_categories)
            self.assertEqual(1., neck.beta)
        with self.subTest(model_type='bogus'), self.assertRaises(ValueError):
            self._build_neck('bogus')

    @staticmethod
    def _build_neck(model_type):
        return building._build_bottleneck(model_type, latent_dim=32)

    def test_build_networks(self):
        latent_dim = 32
        with self.subTest(model_type='stacked'):
            encoder, decoder = self._build_nets('stacked', latent_dim)
            self.assertIsInstance(encoder, encoders.StackedEncoder)
            self.assertIsInstance(decoder, decoders.StackedDecoder)
            self.assertEqual(latent_dim, encoder.latent_dim)
            self.assertEqual(latent_dim, decoder.latent_dim)
        with self.subTest(model_type='shallow'):
            encoder, decoder = self._build_nets('shallow', latent_dim)
            self.assertIsInstance(encoder, encoders.ShallowEncoder)
            self.assertIsInstance(decoder, decoders.ShallowDecoder)
            self.assertEqual(latent_dim, encoder.latent_dim)
            self.assertEqual(latent_dim, decoder.latent_dim)
        with self.subTest(model_type='vanilla'):
            encoder, decoder = self._build_nets('vanilla', latent_dim)
            self.assertIsInstance(encoder, encoders.DenseEncoder)
            self.assertIsInstance(decoder, decoders.DenseDecoder)
            self.assertEqual(latent_dim, encoder.latent_dim)
            self.assertEqual(latent_dim, decoder.latent_dim)
        with self.subTest(model_type='vae'):
            encoder, decoder = self._build_nets('vae', latent_dim)
            self.assertIsInstance(encoder, encoders.DenseEncoder)
            self.assertIsInstance(decoder, decoders.DenseDecoder)
            self.assertEqual(2 * latent_dim, encoder.latent_dim)
            self.assertEqual(latent_dim, decoder.latent_dim)
        with self.subTest(model_type='beta_vae_strict'):
            encoder, decoder = self._build_nets('beta_vae_strict', latent_dim)
            self.assertIsInstance(encoder, encoders.DenseEncoder)
            self.assertIsInstance(decoder, decoders.DenseDecoder)
            self.assertEqual(2 * latent_dim, encoder.latent_dim)
            self.assertEqual(latent_dim, decoder.latent_dim)

    @staticmethod
    def _build_nets(model_type, latent_dim):
        return building._build_networks(model_type, (1, 32, 32), latent_dim)